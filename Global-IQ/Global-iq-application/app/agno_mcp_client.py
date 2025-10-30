"""
MCP Client for Global IQ
Connects Chainlit app to MCP prediction servers via HTTP
"""

import httpx
from typing import Dict, Any
import logging
from urllib.parse import urlparse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GlobalIQAgentSystem:
    """
    HTTP-based client for Global IQ MCP servers
    Manages communication with compensation and policy prediction servers
    """

    # Whitelist of allowed hosts to prevent SSRF attacks
    ALLOWED_HOSTS = {"localhost", "127.0.0.1", "::1"}

    def __init__(
        self,
        compensation_server_url: str = "http://localhost:8081",
        policy_server_url: str = "http://localhost:8082",
        timeout: float = 10.0
    ):
        """
        Initialize the MCP client

        Args:
            compensation_server_url: URL for compensation server (default: http://localhost:8081)
            policy_server_url: URL for policy server (default: http://localhost:8082)
            timeout: Request timeout in seconds (default: 10.0)

        Raises:
            ValueError: If URLs are invalid or point to disallowed hosts
        """
        # Validate URLs to prevent SSRF attacks
        self.compensation_server_url = self._validate_url(compensation_server_url, "compensation")
        self.policy_server_url = self._validate_url(policy_server_url, "policy")
        self.timeout = min(timeout, 30.0)  # Cap at 30 seconds

        logger.info(f"MCP Client initialized - Compensation: {compensation_server_url}, Policy: {policy_server_url}")

    def _validate_url(self, url: str, server_name: str) -> str:
        """
        Validate URL to prevent SSRF attacks

        Args:
            url: URL to validate
            server_name: Name of server for error messages

        Returns:
            Validated URL

        Raises:
            ValueError: If URL is invalid or points to disallowed host
        """
        try:
            parsed = urlparse(url)

            # Check scheme
            if parsed.scheme not in ("http", "https"):
                raise ValueError(f"{server_name} URL must use http or https scheme")

            # Check host
            if parsed.hostname not in self.ALLOWED_HOSTS:
                raise ValueError(
                    f"{server_name} URL host '{parsed.hostname}' not in allowed hosts: {self.ALLOWED_HOSTS}"
                )

            # Check port is in valid range
            if parsed.port is not None and (parsed.port < 1 or parsed.port > 65535):
                raise ValueError(f"{server_name} URL port must be between 1 and 65535")

            return url

        except Exception as e:
            logger.error(f"Invalid {server_name} URL: {url} - {str(e)}")
            raise ValueError(f"Invalid {server_name} server URL: {str(e)}")

    async def predict_compensation(
        self,
        origin_location: str,
        destination_location: str,
        current_salary: float,
        currency: str = "USD",
        assignment_duration: str = "12 months",
        job_level: str = "Manager",
        family_size: int = 1,
        housing_preference: str = "Company-provided"
    ) -> Dict[str, Any]:
        """
        Get compensation prediction from MCP server

        Args:
            origin_location: Current location (City, Country)
            destination_location: Destination (City, Country)
            current_salary: Current annual salary
            currency: Currency code
            assignment_duration: Duration of assignment
            job_level: Job level/title
            family_size: Number of family members
            housing_preference: Housing preference

        Returns:
            Structured compensation prediction with breakdowns and recommendations
        """
        try:
            logger.info(f"Requesting compensation prediction: {origin_location} -> {destination_location}")

            # Prepare request payload
            payload = {
                "origin_location": origin_location,
                "destination_location": destination_location,
                "current_salary": current_salary,
                "currency": currency,
                "assignment_duration": assignment_duration,
                "job_level": job_level,
                "family_size": family_size,
                "housing_preference": housing_preference
            }

            # Make HTTP POST request to compensation server
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.compensation_server_url}/predict",
                    json=payload
                )
                response.raise_for_status()

                result = response.json()
                logger.info("Compensation prediction successful")
                return result

        except httpx.TimeoutException:
            logger.error(f"Compensation server timeout after {self.timeout}s")
            return {
                "status": "error",
                "error": "service_timeout",
                "message": "The compensation service is currently unavailable. Please try again later."
            }
        except httpx.HTTPStatusError as e:
            logger.error(f"Compensation server returned HTTP {e.response.status_code}: {e.response.text}")
            return {
                "status": "error",
                "error": "service_error",
                "message": "The compensation service encountered an error. Please try again later."
            }
        except Exception as e:
            logger.error(f"Compensation prediction failed: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "error": "prediction_failed",
                "message": "Unable to generate compensation prediction. Please try again later."
            }

    async def analyze_policy(
        self,
        origin_country: str,
        destination_country: str,
        assignment_type: str = "Long-term",
        duration: str = "12 months",
        job_title: str = "Manager"
    ) -> Dict[str, Any]:
        """
        Get policy analysis from MCP server

        Args:
            origin_country: Origin country
            destination_country: Destination country
            assignment_type: Type of assignment
            duration: Duration of assignment
            job_title: Job title

        Returns:
            Structured policy analysis with requirements and compliance info
        """
        try:
            logger.info(f"Requesting policy analysis: {origin_country} -> {destination_country}")

            # Prepare request payload
            payload = {
                "origin_country": origin_country,
                "destination_country": destination_country,
                "assignment_type": assignment_type,
                "duration": duration,
                "job_title": job_title
            }

            # Make HTTP POST request to policy server
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.policy_server_url}/analyze",
                    json=payload
                )
                response.raise_for_status()

                result = response.json()
                logger.info("Policy analysis successful")
                return result

        except httpx.TimeoutException:
            logger.error(f"Policy server timeout after {self.timeout}s")
            return {
                "status": "error",
                "error": "service_timeout",
                "message": "The policy service is currently unavailable. Please try again later."
            }
        except httpx.HTTPStatusError as e:
            logger.error(f"Policy server returned HTTP {e.response.status_code}: {e.response.text}")
            return {
                "status": "error",
                "error": "service_error",
                "message": "The policy service encountered an error. Please try again later."
            }
        except Exception as e:
            logger.error(f"Policy analysis failed: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "error": "analysis_failed",
                "message": "Unable to complete policy analysis. Please try again later."
            }

    def health_check(self) -> Dict[str, bool]:
        """
        Check health of both MCP servers (synchronous)

        Returns:
            Dict with health status of each server:
            {
                "compensation_server": bool,
                "policy_server": bool
            }
        """
        import requests

        status = {
            "compensation_server": False,
            "policy_server": False
        }

        # Check compensation server
        try:
            response = requests.get(
                f"{self.compensation_server_url}/health",
                timeout=2.0
            )
            status["compensation_server"] = (response.status_code == 200)
        except Exception as e:
            logger.debug(f"Compensation server health check failed: {e}")

        # Check policy server
        try:
            response = requests.get(
                f"{self.policy_server_url}/health",
                timeout=2.0
            )
            status["policy_server"] = (response.status_code == 200)
        except Exception as e:
            logger.debug(f"Policy server health check failed: {e}")

        return status
