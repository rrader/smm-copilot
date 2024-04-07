from kivy.properties import ListProperty
from kivymd.uix.screen import MDScreen
from kivy.clock import Clock

from smm.ui.projects import ProjectListItem


class BaseScreen(MDScreen):
    pass


class HomeScreen(MDScreen):

    projects = ListProperty()

    def on_projects(self, instance, value):
        self.ids.list_of_projects.clear_widgets()
        for prj in value:
            prj_ = prj.copy()
            self.ids.list_of_projects.add_widget(
                ProjectListItem(
                    name=prj.name,
                    on_release=lambda x, prj=prj_: self.app.on_project_select(prj)
                )
            )


class SettingsScreen(MDScreen):
    pass
