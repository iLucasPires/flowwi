"""Google Drive service using official google-api-python-client."""

import io
import logging
import secrets

from django.conf import settings
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from lib.clients import redis_client

logger = logging.getLogger(__name__)

STATE_PREFIX = "oauth:drive:state:"
STATE_TTL = 600


class GoogleDriveService:
    """Google Drive OAuth2 and file operations via official SDK."""

    SCOPES = ["https://www.googleapis.com/auth/drive.file"]

    # ── OAuth State (Redis) ───────────────────────────────────────────────────

    def generate_state(self, workplace_id: str, user_id: int) -> str:
        token = secrets.token_urlsafe(32)

        redis_client.setex(
            name=f"{STATE_PREFIX}{token}",
            time=STATE_TTL,
            value=f"{workplace_id}:{user_id}",
        )

        return token

    def verify_state(self, state: str) -> tuple[str, int] | None:
        key = f"{STATE_PREFIX}{state}"
        payload = redis_client.get(key)

        if not payload:
            return None

        redis_client.delete(key)

        try:
            workplace_id, user_id = payload.rsplit(":", 1)

            return workplace_id, int(user_id)
        except (ValueError, TypeError):
            return None

    def mark_state_completed(self, state: str) -> None:
        redis_client.setex(f"{STATE_PREFIX}{state}:done", STATE_TTL, "1")

    def is_state_completed(self, state: str) -> bool:
        return redis_client.exists(f"{STATE_PREFIX}{state}:done") == 1

    # ── OAuth Flow ────────────────────────────────────────────────────────────

    def get_flow(self, request):
        redirect_uri = request.build_absolute_uri("/api/google-drive/callback")

        return Flow.from_client_config(
            client_config={
                "web": {
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET_KEY,
                    "auth_uri": "https://accounts.google.com/o/oauth2/v2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                }
            },
            scopes=self.SCOPES,
            redirect_uri=redirect_uri,
        )

    def get_auth_url(self, request, state: str) -> str:
        flow = self.get_flow(request)

        url, _ = flow.authorization_url(
            state=state,
            access_type="offline",
            prompt="consent",
        )

        redis_client.setex(
            f"{STATE_PREFIX}{state}:verifier",
            STATE_TTL,
            flow.code_verifier,
        )

        return url

    def exchange_code(self, code: str, request, state: str) -> dict:
        flow = self.get_flow(request)
        verifier = redis_client.get(f"{STATE_PREFIX}{state}:verifier")

        if verifier:
            flow.code_verifier = verifier

        flow.fetch_token(code=code)
        creds = flow.credentials

        return {
            "access_token": creds.token,
            "refresh_token": creds.refresh_token or "",
            "expires_at": creds.expiry,
        }

    # ── Build Drive client from connection ────────────────────────────────────

    def _get_credentials(self, connection) -> Credentials:
        expiry = connection.token_expires_at

        if expiry and expiry.tzinfo is not None:
            expiry = expiry.replace(tzinfo=None)

        creds = Credentials(
            token=connection.access_token,
            refresh_token=connection.refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=settings.GOOGLE_CLIENT_ID,
            client_secret=settings.GOOGLE_CLIENT_SECRET_KEY,
            expiry=expiry,
        )

        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            connection.access_token = creds.token
            connection.token_expires_at = creds.expiry
            connection.save(update_fields=["access_token", "token_expires_at"])

        return creds

    def _build_service(self, connection):
        creds = self._get_credentials(connection)

        return build("drive", "v3", credentials=creds)

    # ── Drive Operations ──────────────────────────────────────────────────────

    def list_files(self, connection) -> list[dict]:
        service = self._build_service(connection)
        q = "trashed = false"

        if connection.folder_id:
            q = f"'{connection.folder_id}' in parents and trashed = false"

        result = (
            service.files()
            .list(
                q=q,
                fields="files(id,name,mimeType,size,modifiedTime,thumbnailLink,webViewLink)",
                pageSize=50,
                orderBy="modifiedTime desc",
            )
            .execute()
        )
        return result.get("files", [])

    def upload_file(self, connection, file_content: bytes, file_name: str, mime_type: str) -> dict:
        """Upload file to Google Drive. Returns {file_id, name, mime_type, web_view_link}."""
        service = self._build_service(connection)

        file_metadata = {"name": file_name}

        if connection.folder_id:
            file_metadata["parents"] = [connection.folder_id]

        media = MediaIoBaseUpload(
            io.BytesIO(file_content),
            mimetype=mime_type,
            resumable=True,
        )

        result = (
            service.files()
            .create(
                body=file_metadata,
                media_body=media,
                fields="id,name,mimeType,webViewLink",
            )
            .execute()
        )

        service.permissions().create(
            fileId=result["id"],
            body={
                "type": "anyone",
                "role": "reader",
            },
        ).execute()

        return {
            "file_id": result["id"],
            "name": result["name"],
            "mime_type": result["mimeType"],
            "web_view_link": f"https://lh3.googleusercontent.com/d/{result['id']}",
        }

    def delete_file(self, connection, file_id: str) -> None:
        """Delete a file from Google Drive."""
        service = self._build_service(connection)
        service.files().delete(fileId=file_id).execute()
