from flask import Flask, request, jsonify
import requests
import os
import tempfile
from git import Repo
from nbconvert.exporters import PythonExporter
import openai
import nbformat
import tiktoken 


non_code_extensions = (
    ".md",  # Markdown files
    ".txt",  # Text files
    ".csv",  # Comma-separated values
    ".json",  # JSON files
    ".yml",  # YAML files
    ".yaml",  # YAML files
    ".xml",  # XML files
    ".ini",  # Configuration files
    ".cfg",  # Configuration files
    ".conf",  # Configuration files
    ".properties",  # Java properties files
    ".log",  # Log files
    ".gitignore",  # Git ignore rules
    ".editorconfig",  # Editor configuration files
    ".dockerignore",  # Docker ignore rules
    ".prettierignore",  # Prettier ignore rules
    ".prettierrc",  # Prettier configuration files
    ".eslintrc",  # ESLint configuration files
    ".eslintignore",  # ESLint ignore rules
    ".stylelintrc",  # Stylelint configuration files
    ".stylelintignore",  # Stylelint ignore rules
    ".npmignore",  # NPM ignore rules
    ".npmrc",  # NPM configuration files
    ".lock",  # Dependency lock files
    ".LICENSE",  # License files
    ".license",  # License files
    ".LICENSE-MIT",  # MIT License files
    ".LICENSE-APACHE",  # Apache License files
    ".gitmodules",  # Git submodule configuration files
    ".gitattributes",  # Git attribute files
    ".gitconfig",  # Git configuration files
    ".rst",  # reStructuredText files
    ".pdf",  # Portable Document Format files
    ".ppt",  # PowerPoint presentation files
    ".pptx",  # PowerPoint presentation files (XML-based)
    ".doc",  # Word document files
    ".docx",  # Word document files (XML-based)
    ".xls",  # Excel spreadsheet files
    ".xlsx",  # Excel spreadsheet files (XML-based)
    ".rtf",  # Rich Text Format files
    ".jpg",  # JPEG image files
    ".jpeg",  # JPEG image files
    ".png",  # PNG image files
    ".gif",  # GIF image files
    ".bmp",  # Bitmap image files
    ".ico",  # Icon files
    ".svg",  # Scalable Vector Graphics files
    ".psd",  # Adobe Photoshop files
    ".ai",  # Adobe Illustrator files
    ".eps",  # Encapsulated PostScript files
    ".tif",  # TIFF image files
    ".tiff",  # TIFF image files
    ".zip",  # ZIP archive files
    ".tar",  # TAR archive files
    ".gz",  # GZIP archive files
    ".bz2",  # BZIP2 archive files
    ".7z",  # 7-Zip archive files
    ".rar",  # RAR archive files
    ".iso",  # ISO image files
    ".img",  # Disk image files
    ".bin",  # Binary files
    ".dat",  # Data files
    ".bak",  # Backup files
    ".tmp",  # Temporary files
    ".swp",  # Swap files
    ".swo",  # Swap files
    ".readme",  # Readme files
    ".changelog",  # Changelog files
    ".changes",  # Changelog files
    ".news",  # Changelog files
    ".asciidoc",  # AsciiDoc files
    ".adoc",  # AsciiDoc files
    ".dtd",  # Document Type Definition files
    ".xsd",  # XML Schema Definition files
    ".plist",  # Property List files
    ".toml",  # TOML files
    ".tsv",  # Tab-separated values files
    ".ods",  # OpenDocument Spreadsheet files
    ".odt",  # OpenDocument Text files
    ".ott",  # OpenDocument Text Template files
    ".odp",  # OpenDocument Presentation files
    ".otp",  # OpenDocument Presentation Template files
    ".odg",  # OpenDocument Graphics files
    ".otg",  # OpenDocument Graphics Template files
    ".notebook",  # Jupyter Notebook files
    ".mdx",  # Markdown Extra files
    ".tex",  # LaTeX files
    ".bib",  # BibTeX files
    ".cls",  # LaTeX class files
    ".sty",  # LaTeX style files
    ".vtt",  # WebVTT files
    ".srt",  # SubRip subtitle files
    ".sbv",  # YouTube caption files
    ".ass",  # Advanced SubStation Alpha subtitle files
    ".ssa",  # SubStation Alpha subtitle files
    ".ics",  # iCalendar files
    ".ifb",  # iCalendar free/busy time files
    ".ical",  # iCalendar files
    ".icalendar",  # iCalendar files
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".bmp",
    ".svg",
    ".ipynb",
    ".ttf",
    ".otf",
    ".woff",
    ".woff2",
    ".eot",
    ".pfa",
    ".pfb",
    ".afm",
    ".pfm",
    ".fon",
    ".fnt",
    ".svg",
    ".sfd",
    ".3ds",  # 3D Studio Max files
    ".obj",  # Wavefront Object files
    ".fbx",  # Autodesk FBX files
    ".dae",  # COLLADA files
    ".stl",  # Stereolithography files
    ".ply",  # Polygon File Format (Stanford Triangle Format)
    ".blend",  # Blender files
    ".max",  # 3D Studio Max files
    ".ma",  # Maya ASCII files
    ".mb",  # Maya Binary files
    ".c4d",  # Cinema 4D files
    ".lwo",  # LightWave Object files
    ".lw",  # LightWave files
    ".lws",  # LightWave Scene files
    ".ase",  # ASCII Scene Export files
    ".x",  # DirectX files
    ".gltf",  # GL Transmission Format files
    ".glb",  # Binary GL Transmission Format files
    ".vox",  # MagicaVoxel files
    ".step",  # STEP files
    ".stp",  # STEP files
    ".iges",  # IGES files
    ".igs",  # IGES files
    ".vrml",  # VRML files
    ".wrl",  # VRML files
    ".x3d",  # X3D files
    ".x3db",  # X3D Binary files
    ".x3dv",  # X3D Classic VRML files
)


app = Flask(__name__)


# routes
@app.route("/analyze", methods=["GET"])
def analyze():
    github_url = request.args.get("github_url")
    result = analyze_repositories(github_url)
    return jsonify(result)


def fetch_repositories(github_url):
    username = github_url.split("/")[-1]
    api_url = f"https://api.github.com/users/{username}/repos"
    response = requests.get(api_url)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(
            f"Failed to fetch repositories for user {username}: {response.text}"
        )


def preprocess_code_chunks(repo_url, max_tokens=2048):
    repo_name = repo_url.split("/")[-1].split(".")[0]
    temp_dir = tempfile.mkdtemp()
    local_path = os.path.join(temp_dir, repo_name)

    # Clone the repository
    Repo.clone_from(repo_url, local_path)

    print(f"Cloned repository {repo_url} to {local_path}")
    # Convert Jupyter notebooks to Python scripts
    exporter = PythonExporter()
    for root, dirs, files in os.walk(local_path):
        # Ignore node_modules and directories starting with .
        dirs[:] = [d for d in dirs if not (d.startswith(".") or d == "node_modules")]

        for file in files:
            if file.endswith(".ipynb"):
                file_path = os.path.join(root, file)
                with open(file_path) as f:
                    nb_node = nbformat.read(f, as_version=4)
                script, _ = exporter.from_notebook_node(nb_node)
                with open(file_path.replace(".ipynb", ".py"), "w") as f:
                    f.write(script)

    # Read all code files and create chunks of code up to max_tokens
    code_chunks = []
    current_chunk = ""
    current_tokens = 0
    for root, dirs, files in os.walk(local_path):
        # Ignore node_modules and directories starting with .
        dirs[:] = [
            d
            for d in dirs
            if not (
                d.startswith(".")
                or d == "node_modules"
                or d == "venv"
                or d == "env"
                or d == "virtualenv"
                or d == "assets"
                or d == "static"
                or d == "build"
                or d == "dist"
                or d == "target"
            )
        ]

        for file in files:
            file_path = os.path.join(root, file)
            if (
                not file.lower().endswith(non_code_extensions)
                and not file.startswith(".")
                and file
                not in [
                    "LICENSE",
                    "license",
                ]
                and not is_binary(file_path)
            ):
                with open(file_path) as f:
                    print("Processing file:", file_path)
                    file_code = f.read()
                    tokens_in_file = len(file_code.split())

                    if current_tokens + tokens_in_file <= max_tokens:
                        current_chunk += f"File: {file}\n"  # Append the file name
                        current_chunk += file_code + "\n"
                        current_tokens += tokens_in_file
                    else:
                        code_chunks.append(current_chunk)
                        current_chunk = f"File: {file}\n"  # Append the file name
                        current_chunk += file_code + "\n"
                        current_tokens = tokens_in_file

    # Add the last chunk if it's not empty
    if current_chunk.strip():
        code_chunks.append(current_chunk)
    return code_chunks


def analyze_code_with_gpt(code_chunks, max_tokens=2048):
    openai.api_key = "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"
    total_complexity = 0
    analyzed_chunks = 0
    # Analyze each code chunk
    for i, code_chunk in enumerate(code_chunks):
        print("Analyzing code chunk: ", i + 1, " out of ", len(code_chunks))
        prompt = f"Rate the technical complexity of the following Python code on a scale of 1 to 10:\n\n{code_chunk}\n\nRating:"
        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=prompt,
            max_tokens=10,
            n=1,
            stop=None,
            temperature=0.5,
        )
        try:
            rating = float(response.choices[0].text.strip())
            total_complexity += rating
            analyzed_chunks += 1
        except ValueError:
            pass
    if analyzed_chunks > 0:
        return total_complexity / analyzed_chunks
    else:
        return None


def analyze_repositories(github_url):
    repos = fetch_repositories(github_url)
    max_complexity = -1
    most_complex_repo = None
    gpt_analysis = ""

    for repo in repos:
        repo_url = repo["html_url"]
        code_chunks = preprocess_code_chunks(repo_url)
        print(len(code_chunks), " code chunks found")
        complexity = analyze_code_with_gpt(code_chunks)
        print("Complexity score of ", repo["name"], ": ", complexity)

        if complexity is not None and complexity > max_complexity:
            max_complexity = complexity
            most_complex_repo = repo
            gpt_analysis = complexity

    return {
        "most_complex_repository": most_complex_repo["html_url"],
        "gpt_analysis": gpt_analysis,
    }


def is_binary(file_path):
    with open(file_path, "rb") as f:
        for _ in range(1024):
            chunk = f.read(1024)
            if b"\0" in chunk:
                return True
    return False


if __name__ == "__main__":
    app.run(debug=True)
