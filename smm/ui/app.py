import os

from kivy.lang import Builder
from kivy.properties import StringProperty, ObjectProperty
from kivy.uix.widget import Widget
from kivymd.app import MDApp
from kivymd.uix.button import MDButton
from kivymd.uix.button import MDButtonText
from kivymd.uix.dialog import (
    MDDialog,
    MDDialogIcon,
    MDDialogHeadlineText,
    MDDialogSupportingText,
    MDDialogButtonContainer,
    MDDialogContentContainer,
)
from kivymd.uix.divider import MDDivider
from kivymd.uix.navigationbar import MDNavigationBar, MDNavigationItem
from kivymd.uix.textfield import MDTextField, MDTextFieldLeadingIcon, MDTextFieldHintText, MDTextFieldHelperText

from smm.ui.projects import Projects
from smm.ui.settings import Settings
from smm.ui.screens import *

# path of the kv file in the same directory as this file
PATH = os.path.dirname(os.path.realpath(__file__))
KV_PATH = os.path.join(PATH, "app.kv")


class BaseMDNavigationItem(MDNavigationItem):
    icon = StringProperty()
    text = StringProperty()


class MainApp(MDApp):
    project = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "AutoSMM"
        self.settings = Settings()
        self.projects = Projects()
        self.project = self.projects.get_default()
        self.dialog = None

    def build(self):
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Orange"  # "Purple", "Red"

        return Builder.load_file(KV_PATH)

    def on_project_select(self, project):
        self.project = project
        self.projects.set_default(project.name)

    def on_switch_tabs(
        self,
        bar: MDNavigationBar,
        item: MDNavigationItem,
        item_icon: str,
        item_text: str,
    ):
        self.root.ids.screen_manager.current = item_text

    def show_project_settings(self):
        self.root.ids.screen_manager.current = "Project Settings"

    def on_start(self):
        super().on_start()

    def create_project(self):

        def do_create_project(button):
            project_name = self.dialog.get_ids()['project_name_field'].text
            self.projects.add_empty(project_name)
            self.dialog.dismiss()

        self.dialog = MDDialog(
            # ----------------------------Icon-----------------------------
            MDDialogIcon(
                icon="account",
            ),
            # -----------------------Headline text-------------------------
            MDDialogHeadlineText(
                text="Create project",
            ),
            # -----------------------Supporting text-----------------------
            MDDialogSupportingText(
                text="Enter project name to create a new project.",
            ),
            # -----------------------Custom content------------------------
            MDDialogContentContainer(
                MDDivider(),

                MDTextField(
                    MDTextFieldLeadingIcon(icon="account"),
                    MDTextFieldHintText(text="Project name"),
                    MDTextFieldHelperText(
                        text="Enter project name",
                        mode="persistent",
                    ),
                    id="project_name_field",
                ),
                MDDivider(),
                orientation="vertical",
            ),
            MDDialogButtonContainer(
                Widget(),
                MDButton(
                    MDButtonText(text="Cancel"),
                    style="text",
                    on_release=lambda x: self.dialog.dismiss(),
                ),
                MDButton(
                    MDButtonText(text="Ok"),
                    style="text",
                    on_release=do_create_project,
                ),
                spacing="8dp",
            ),
        )
        self.dialog.open()


if __name__ == "__main__":
    MainApp().run()
