from kivy.event import EventDispatcher
from kivy.properties import StringProperty, DictProperty, ListProperty
from kivymd.uix.list import MDListItem
from kivy.storage.jsonstore import JsonStore


class ProjectListItem(MDListItem):
    name = StringProperty()


class Projects(EventDispatcher):
    """SMM Projects stored in kivy json storage"""

    projects = ListProperty()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.storage = JsonStore('projects.json')

        self.projects = self.list()

    def add_empty(self, project_name):
        self.projects.append(Project(project_name, {}, self))

    def save_project(self, project):
        self.storage.put(project.name, value=project.value)

    def on_projects(self, instance, value):
        for project in value:
            self.save_project(project)

    def get_default(self):
        if "__default" in self.storage:
            return self.get(self.storage.get("__default")['value'])

    def set_default(self, project_name):
        self.storage.put("__default", value=project_name)

    def list(self):
        return [
            self.get(project_name)
            for project_name in self.storage.store_keys()
            if project_name != "__default"
        ]

    def get(self, project_name):
        return Project(project_name, self.storage.get(project_name)['value'], self)


class Project(EventDispatcher):
    """SMM Project"""

    value = DictProperty()
    system_prompt = StringProperty()

    def __init__(self, name, value, projects, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name
        self.projects = projects
        self.value = value

        self.system_prompt = value.get("system_prompt", "")

    def to_dict(self):
        return {
            "name": self.name,
            "value": self.value,
        }

    def copy(self):
        return Project(self.name, self.value.copy(), self.projects)

    def on_value(self, instance, value):
        self.projects.save_project(self)

    def on_system_prompt(self, instance, system_prompt):
        self.value["system_prompt"] = system_prompt
