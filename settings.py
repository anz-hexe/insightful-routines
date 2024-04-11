from pathlib import Path


def create_data_folder(folder_name):
    project_path = Path(folder_name)
    project_path.mkdir(parents=True, exist_ok=True)

    gitignore_content = """# Ignore all files/directories
*
"""
    with open(project_path / ".gitignore", "w") as gitignore_file:
        gitignore_file.write(gitignore_content)

    print(f"Project folder '{folder_name}' and .gitignore file created successfully.")
