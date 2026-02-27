from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun

@tool("read_file")
def read_file(file_path: str) -> str:
    '''Reads the content of a file.'''
    try:
        with open(file_path, 'r') as f:
            return f.read()
    except Exception as e:
        return str(e)

@tool("write_file")
def write_file(file_path: str, content: str) -> str:
    '''Writes the content of a file.'''
    try:
        with open(file_path, 'w') as f:
            f.write(content)
        return "File written successfully."
    except Exception as e:
        return str(e)

@tool("list_files")
def list_files(directory: str) -> str:
    '''Lists the files in a directory.'''
    try:
        with os.scandir(directory) as it:
            return "\n".join([e.name for e in it])
    except Exception as e:
        return str(e)


@tool("run_command")
def run_command(command: str) -> str:
    '''Runs a command in the terminal.'''
    try:
        return subprocess.check_output(command, shell=True).decode('utf-8')
    except Exception as e:
        return str(e)
    
@tool("web_search")
def web_search(query: str) -> str:
    '''Searches the web for the given query.'''
    search = DuckDuckGoSearchRun()
    try:
        return search.invoke(query)
    except Exception as e:
        return str(e)

tools = [read_file, write_file, list_files, run_command, web_search]
