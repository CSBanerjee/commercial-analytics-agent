
import uuid
import subprocess
import tempfile
import os
import signal


class PythonExecutor:

    def __init__(
        self,
        docker_image="commercial-analytics-sandbox",
        dataset_path="commercial_sales_data_usd.csv"
    ):
        self.docker_image = docker_image
        self.dataset_path = os.path.abspath(dataset_path)

    def execute(self, python_code):

        temp_file_path = None
        container_name = f"analytics-{uuid.uuid4().hex[:12]}"

        # 1. Validate dataset
        if not os.path.isfile(self.dataset_path):
            return {
                "status": "error",
                "result": None,
                "error": f"Dataset not found: {self.dataset_path}"
            }

        try:
            # 2. Create temporary Python file inside project directory
            with tempfile.NamedTemporaryFile(
                mode="w",
                suffix=".py",
                delete=False,
                dir=os.path.dirname(self.dataset_path)
            ) as temp_file:

                temp_file.write(python_code)
                temp_file_path = temp_file.name

            # Allow sandboxuser (UID 1000) to read the file
            os.chmod(temp_file_path, 0o644)

            # 3. Prepare Docker command
            docker_command = [
                "docker",
                "run",
                "--name", container_name,
                "--network", "none",
                "--memory", "256m",
                "--cpus", "0.5",
                "--pids-limit", "64",
                "--read-only",
                "--tmpfs", "/tmp:rw,noexec,nosuid,size=16m",
                "-v",
                f"{temp_file_path}:/sandbox/analysis.py:ro",
                "-v",
                f"{self.dataset_path}:/sandbox/commercial_sales_data_usd.csv:ro",
                self.docker_image,
                "python",
                "/sandbox/analysis.py"
            ]

            # 4. Start Docker process
            process = subprocess.Popen(
                docker_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                start_new_session=True
            )

            try:
                stdout, stderr = process.communicate(timeout=30)

            except subprocess.TimeoutExpired:

                # Terminate Docker CLI process group
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass

                process.communicate()
                raise

            # 5. Return execution result
            if process.returncode == 0:
                return {
                    "status": "success",
                    "result": stdout.strip(),
                    "error": None
                }

            return {
                "status": "error",
                "result": None,
                "error": stderr.strip()
            }

        except subprocess.TimeoutExpired:

            return {
                "status": "error",
                "result": None,
                "error": "Python execution exceeded the 30-second limit."
            }

        except Exception as e:

            return {
                "status": "error",
                "result": None,
                "error": str(e)
            }

        finally:

            # 6. Remove Docker container
            try:
                subprocess.run(
                    ["docker", "rm", "-f", container_name],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
            except (subprocess.TimeoutExpired, OSError):
                pass

            # 7. Remove temporary Python file
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.remove(temp_file_path)
                except OSError:
                    pass
