from langchain_core.tools import tool
from pathlib import Path
import subprocess


class FileSystemTools:
    def __init__(self,SandBox:str):
        self.SandBox = Path(SandBox).resolve()
        self.SandBox.mkdir(parents=True,exist_ok=True)
        self.SandBox.mkdir(parents=True, exist_ok=True)

    def _safe_path(self, relative_path: str) -> Path:
        """
        Resolve a path and guarantee that it staysinside the PlayGround SandBox.
        """
        target = (self.SandBox / relative_path).resolve()
        if not target.is_relative_to(self.SandBox):
            raise PermissionError(f"Access outside SandBox is not allowed: {relative_path}")
        return target

    def create_file(self,path: str,content: str = "") -> dict:
        """Create a new file at the given sandbox-relative path with optional content."""
        file_path = self._safe_path(path)
        if file_path.exists():
            return {
                "success": False,
                "error": f"File already exists: {path}"
            }
        
        file_path.parent.mkdir(parents=True,exist_ok=True)
        file_path.write_text(content,encoding="utf-8")
        return {
            "success": True,
            "action": "create_file",
            "path": path
        }

    def read_file(self, path: str) -> dict:
        """Read and return the contents of an existing file at the given sandbox-relative path."""
        file_path = self._safe_path(path)
        if not file_path.exists():
            return {
                "success": False,
                "error": f"File does not exist: {path}"
            }
        
        if not file_path.is_file():
            return {
                "success": False,
                "error": f"Path is not a file: {path}"
            }

        content = file_path.read_text(encoding="utf-8")
        return {
            "success": True,
            "action": "read_file",
            "path": path,
            "content": content
        }

    def update_file(self,path: str,content: str) -> dict:
        """Replace the contents of an existing file at the given sandbox-relative path."""
        file_path = self._safe_path(path)
        if not file_path.exists():
            return {
                "success": False,
                "error": f"File does not exist: {path}"
            }
        
        if not file_path.is_file():
            return {
                "success": False,
                "error": f"Path is not a file: {path}"
            }

        file_path.write_text(content,encoding="utf-8")
        return {
            "success": True,
            "action": "update_file",
            "path": path
        }

    def create_folder(self, path: str) -> dict:
        """Create a new folder at the given sandbox-relative path."""
        if folder_path.exists():
            if folder_path.is_dir():
                return {
                    "success": True,
                    "action": "create_folder",
                    "path": path,
                    "already_exists": True
                }

            return {
                "success": False,
                "error": f"A file already exists at: {path}"
            }

        
        folder_path = self._safe_path(path)
        if folder_path.exists():
            return {
                "success": False,
                "error": f"Folder already exists: {path}"
            }

        folder_path.mkdir(parents=True,exist_ok=False)
        return {
            "success": True,
            "action": "create_folder",
            "path": path
        }

    def list_folder(self, path: str = ".") -> dict:
        """List the files and folders directly inside the given sandbox-relative directory."""
        folder_path = self._safe_path(path)
        if not folder_path.exists():
            return {
                "success": False,
                "error": f"Folder does not exist: {path}"
            }
        
        if not folder_path.is_dir():
            return {
                "success": False,
                "error": f"Path is not a folder: {path}"
            }

        items = []

        for item in folder_path.iterdir():
            relative_path = str(item.relative_to(self.SandBox))
            items.append({
                "name": item.name,
                "path": relative_path,
                "type": "folder"
                if item.is_dir()
                else "file"
            })

        return {
            "success": True,
            "action": "list_folder",
            "path": path,
            "items": items
        }

    def update_folder(self,old_path: str,new_path: str) -> dict:
        """Rename or move a folder from old_path to new_path within the sandbox."""
        old_folder = self._safe_path(old_path)
        new_folder = self._safe_path(new_path)

        if not old_folder.exists():
            return {
                "success": False,
                "error": f"Folder does not exist: {old_path}"
            }

        if not old_folder.is_dir():
            return {
                "success": False,
                "error": f"Path is not a folder: {old_path}"
            }

        if new_folder.exists():
            return {
                "success": False,
                "error": f"Destination already exists: {new_path}"
            }

        old_folder.rename(new_folder)

        return {
            "success": True,
            "action": "update_folder",
            "old_path": old_path,
            "new_path": new_path
        }

    def find_file(self, name: str) -> dict:
        """Recursively search all sandbox subfolders for a file with the given name."""
        matches = []

        for path in self.SandBox.rglob(name):
            if path.is_file():
                matches.append(
                    str(path.relative_to(self.SandBox))
                )

        if not matches:
            return {
                "success": False,
                "error": f"File not found: {name}",
                "matches": []
            }

        return {
            "success": True,
            "action": "find_file",
            "name": name,
            "matches": matches
        }
    
    def open_file(self, path: str) -> dict:
        """Open an existing file using the operating system's default application."""
        file_path = self._safe_path(path)

        if not file_path.exists():
            return {
                "success": False,
                "error": f"File does not exist: {path}"
            }

        try:
            subprocess.run(
                ["open", str(file_path)],
                check=True
            )

            return {
                "success": True,
                "action": "open_file",
                "path": path
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    