import sys
import os
import github
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QTextEdit, QFileDialog, QMessageBox, QInputDialog

class ProjectConverterApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Project Converter")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()

        self.tree_input = QTextEdit()
        self.tree_input.setPlaceholderText("Paste project hierarchy tree here...")
        self.layout.addWidget(self.tree_input)

        self.select_directory_button = QPushButton("Select Directory")
        self.layout.addWidget(self.select_directory_button)

        self.create_structure_button = QPushButton("Create Structure")
        self.layout.addWidget(self.create_structure_button)

        self.central_widget.setLayout(self.layout)

        self.create_structure_button.clicked.connect(self.show_confirmation_screen)
        self.select_directory_button.clicked.connect(self.select_directory)

    def select_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        self.selected_directory = directory

    def show_confirmation_screen(self):
        # Get the project hierarchy tree from the input text
        tree_text = self.tree_input.toPlainText()
        tree_structures = tree_text.strip().split('\n\n')

        # Create a confirmation message with the project structure
        confirmation_message = "You are about to create the following directory structures:\n\n"
        for structure in tree_structures:
            confirmation_message += structure + '\n\n'

        # Ask for GitHub integration and repository creation options
        github_integration = QMessageBox.question(self, "GitHub Integration", "Do you want to integrate with GitHub?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if github_integration == QMessageBox.StandardButton.Yes:
            github_repo_name, ok = QInputDialog.getText(self, "GitHub Repository", "Enter the GitHub repository name:")
            if ok and github_repo_name.strip():
                confirmation_message += f"\nGitHub Repository Name: {github_repo_name}\n"

                github_create_repo = QMessageBox.question(self, "GitHub Repository Creation", f"Do you want to create a GitHub repository named '{github_repo_name}'?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

                if github_create_repo == QMessageBox.StandardButton.Yes:
                    self.create_structure(tree_structures, True, github_repo_name)
                else:
                    self.create_structure(tree_structures, False, None)
            else:
                self.create_structure(tree_structures, False, None)
        else:
            self.create_structure(tree_structures, False, None)

    def create_structure(self, tree_structures, github_integration, github_repo_name):
        try:
            # Check if a directory is selected
            if hasattr(self, 'selected_directory'):
                for structure in tree_structures:
                    # Get the lines for each structure
                    tree_lines = structure.strip().split('\n')
                    # Extract the directory name from the first line
                    dir_name = tree_lines[0]
                    # Create the directory structure
                    create_directory_structure(os.path.join(self.selected_directory, dir_name), tree_lines[1:])
                
                if github_integration:
                    # GitHub integration logic
                    github_token = input("Enter your GitHub Personal Access Token: ")
                    create_github_repository(github_repo_name, github_token)

                QMessageBox.information(self, "Success", "Directory structure(s) created successfully.")
            else:
                QMessageBox.warning(self, "Warning", "Please select a directory first.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

def create_directory_structure(root_path, tree_lines):
    for line in tree_lines:
        parts = line.split('/')
        current_path = root_path
        for part in parts:
            current_path = os.path.join(current_path, part)
            os.makedirs(current_path, exist_ok=True)

def create_github_repository(repo_name, github_token):
    g = github.Github(github_token)
    user = g.get_user()
    repo = user.create_repo(repo_name)
    print(f"GitHub repository '{repo_name}' created successfully.")

def main():
    app = QApplication(sys.argv)
    window = ProjectConverterApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
