from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.RunScriptAction import RunScriptAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction
import subprocess


class CodeGitExtension(Extension):
    def __init__(self):
        super().__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())


class KeywordQueryEventListener(EventListener):
    def on_event(self, event, extension):
        code_command = extension.preferences["code_command"]
        root_folder = extension.preferences["root_folder"]

        search_command = "find " + root_folder + " -type d -name .git -prune -exec dirname \{} \; | rev | cut -d'/' -f1 | rev"
        
        projects = []
        items = []

        if event.get_argument():
            search_command += f" | grep {event.get_argument()}"
        try:
            result = subprocess.run(
                [
                    'sh',
                    '-c',
                    search_command
                ], capture_output=True, text=True, check=True)
            output = result.stdout.strip()
            if output:
                projects = output.split('\n')
            if len(projects) > 10:
                projects = projects[:10]
        except subprocess.CalledProcessError as e:
            output = f"Error: {e.stderr.strip()}"
        except FileNotFoundError:
            output = "Error: Script not found"

        # Populate items with project names
        for project in projects:
            if project:  # Ensure the project name is not empty
                items.append(ExtensionResultItem(
                    icon='images/icon.png',
                    name=project,
                    description=f'Project: {project}',
                    on_enter=RunScriptAction(f"{code_command} {root_folder}/{project}")
                ))
                
        if not projects:
            items.append(ExtensionResultItem(
                icon='images/icon.png',
                name='No projects found',
                description='No projects found in the root folder',
                on_enter=HideWindowAction()
            ))

        return RenderResultListAction(items)

if __name__ == '__main__':
    CodeGitExtension().run()