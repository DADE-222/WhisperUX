import tkinter as tk
from tkinter import filedialog, messagebox, ttk, scrolledtext
import whisper
import os
import threading

class WhisperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("WhisperUX 2.5 - Transcription Audio")
        self.root.geometry("790x450")  # Redimensionner la fenêtre pour tout afficher
        self.root.resizable(False, False)
        
        # Variables
        self.input_file = None
        self.output_folder = None
        self.model_name = "base"
        self.language = "auto"
        self.linebreaks = True
        self.current_skin = "Light"  # Thème par défaut
        
        # Nouvelles couleurs pour plus de contraste et lisibilité
        self.skins = {
            "Light": {
                "bg": "#F5F5F5",          # Fond gris très clair
                "fg": "#2E2E2E",          # Texte gris foncé
                "console_bg": "#FFFFFF",  # Console en blanc
                "console_fg": "#2E2E2E"   # Texte de la console en gris foncé
            },
            "Dark": {
                "bg": "#2E2E2E",          # Fond gris foncé (pas de noir absolu)
                "fg": "#F5F5F5",          # Texte blanc cassé
                "console_bg": "#2E2E2E",
                "console_fg": "#F5F5F5"
            },
            "Blue": {
                "bg": "#DCEEFF",          # Bleu pâle pour le fond
                "fg": "#003366",          # Bleu foncé pour le texte
                "console_bg": "#DCEEFF",
                "console_fg": "#003366"
            },
            "Green": {
                "bg": "#E0FFE0",          # Vert très pâle
                "fg": "#006600",          # Vert foncé
                "console_bg": "#E0FFE0",
                "console_fg": "#006600"
            },
            "Red": {
                "bg": "#FFDADA",          # Rouge très clair
                "fg": "#800000",          # Rouge bordeaux pour un meilleur contraste
                "console_bg": "#FFDADA",
                "console_fg": "#800000"
            },
        }
        
        # Création de l'interface
        self.create_widgets()
        self.create_menu()
        self.apply_skin(self.current_skin)  # Appliquer le thème par défaut
    
    def create_menu(self):
        menubar = tk.Menu(self.root)
        
        # Menu File
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open", command=self.select_input_file)
        file_menu.add_command(label="Save", command=self.select_output_folder)
        
        # Sous-menu Skins
        skins_menu = tk.Menu(file_menu, tearoff=0)
        for skin_name in self.skins.keys():
            skins_menu.add_command(label=skin_name, command=lambda name=skin_name: self.apply_skin(name))
        file_menu.add_cascade(label="Skins", menu=skins_menu)
        
        menubar.add_cascade(label="File", menu=file_menu)
        
        self.root.config(menu=menubar)
    
    def apply_skin(self, skin_name):
        """Applique un thème de couleur à l'interface."""
        self.current_skin = skin_name
        skin = self.skins[skin_name]
        
        # Appliquer les couleurs principales
        self.root.configure(bg=skin["bg"])
        self.console.configure(bg=skin["console_bg"], fg=skin["console_fg"])
        self.input_path.configure(bg=skin["bg"], fg=skin["fg"])
        self.output_path.configure(bg=skin["bg"], fg=skin["fg"])
        self.progress_label.configure(bg=skin["bg"], fg=skin["fg"])
        
        # Mise à jour des autres widgets (LabelFrame, Button, etc.)
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.LabelFrame):
                widget.configure(bg=skin["bg"], fg=skin["fg"])
                # Mettre à jour les widgets enfants du LabelFrame
                for child in widget.winfo_children():
                    if isinstance(child, tk.Label) or isinstance(child, tk.Button):
                        child.configure(bg=skin["bg"], fg=skin["fg"])
            if isinstance(widget, tk.Button):
                widget.configure(bg=skin["bg"], fg=skin["fg"])
    
    def create_widgets(self):
        # Version
        version_label = tk.Label(self.root, text="Version 2.5", font=("Arial", 8), fg="gray", bg=self.skins[self.current_skin]["bg"])
        version_label.place(x=700, y=430)
        
        # Cadre Console de sortie
        self.console = scrolledtext.ScrolledText(self.root, height=20, width=35, state='disabled')
        self.console.place(x=10, y=10, width=350, height=350)
        
        # Cadre Options
        frame_options = tk.LabelFrame(self.root, text="OPTION", font=("Arial", 10, "bold"))
        frame_options.place(x=370, y=10, width=410, height=150)
        
        tk.Label(frame_options, text="Langue :").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.language_var = tk.StringVar(value="AUTO")
        languages = ["AUTO", "FR", "EN", "ES", "DE", "IT", "PT", "RU", "ZH", "JA"]
        tk.OptionMenu(frame_options, self.language_var, *languages).grid(row=0, column=1, padx=10, pady=5)
        
        tk.Label(frame_options, text="Modèle Whisper :").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.model_var = tk.StringVar(value="BASE")
        tk.OptionMenu(frame_options, self.model_var, "BASE", "SMALL").grid(row=1, column=1, padx=10, pady=5)
        
        tk.Label(frame_options, text="Retour à la ling :").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.linebreaks_var = tk.StringVar(value="OUI")
        tk.OptionMenu(frame_options, self.linebreaks_var, "OUI", "NON").grid(row=2, column=1, padx=10, pady=5)
        
        # Cadre Sélection Fichiers
        frame_files = tk.LabelFrame(self.root, text="Sélection Fichiers")
        frame_files.place(x=370, y=170, width=410, height=170)
        
        tk.Label(frame_files, text="Fichier audio :").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        tk.Button(frame_files, text="FICHIER", command=self.select_input_file).grid(row=0, column=1, padx=10, pady=5)
        self.input_path = tk.Label(frame_files, text="aucun", fg="gray")
        self.input_path.grid(row=0, column=2, padx=10, pady=5, sticky="w")
        
        tk.Label(frame_files, text="Dossier de sortie :").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        tk.Button(frame_files, text="Fichier", command=self.select_output_folder).grid(row=1, column=1, padx=10, pady=5)
        self.output_path = tk.Label(frame_files, text="aucun", fg="gray")
        self.output_path.grid(row=1, column=2, padx=10, pady=5, sticky="w")
        
        # Barre de progression
        self.progress = ttk.Progressbar(self.root, mode='determinate', length=580)
        self.progress.place(x=10, y=370, width=470, height=20)
        self.progress_label = tk.Label(self.root, text="En attente...")
        self.progress_label.place(x=10, y=395)
        
        # Boutons de transcription
        self.transcription_button = tk.Button(self.root, text="LANCER LA TRANSCRIPTION", command=self.start_transcription, borderwidth=2)
        self.transcription_button.place(x=600, y=370, width=180, height=40)
        
        self.cancel_button = tk.Button(self.root, text="ANNULER", command=self.cancel_transcription, state="disabled", borderwidth=2)
        self.cancel_button.place(x=490, y=370, width=100, height=40) 

    def log(self, message):
        self.console.config(state='normal')
        self.console.insert(tk.END, message + "\n")
        self.console.config(state='disabled')
        self.console.yview(tk.END)
    
    def select_input_file(self):
        file = filedialog.askopenfilename(filetypes=[("Fichiers audio", "*.mp3;*.mp4;*.mkv;*.wav")])
        if file:
            self.input_file = file
            self.input_path.config(text=os.path.basename(file), fg="black")
    
    def select_output_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.output_folder = folder
            self.output_path.config(text=folder, fg="black")
    
    def start_transcription(self):
        if not self.input_file or not self.output_folder:
            messagebox.showerror("Erreur", "Veuillez sélectionner un fichier audio et un dossier de sortie.")
            return
        
        self.progress.start(10)
        self.progress_label.config(text="Traitement en cours...")
        self.transcription_button.config(state="disabled")
        self.cancel_button.config(state="normal")
        
        threading.Thread(target=self.process_audio, daemon=True).start()
    
    def cancel_transcription(self):
        self.progress.stop()
        self.progress_label.config(text="Transcription annulée")
        self.transcription_button.config(state="normal")
        self.cancel_button.config(state="disabled")
        self.log("Transcription annulée.")
    
    def process_audio(self):
        try:
            self.log("Chargement du modèle Whisper...")
            model = whisper.load_model(self.model_var.get().lower())
            self.log("Modèle chargé avec succès.")
            
            self.log("Début de la transcription...")
            result = model.transcribe(self.input_file, language=None if self.language_var.get() == "AUTO" else self.language_var.get().lower())
            
            base_name = os.path.basename(self.input_file)
            file_name, _ = os.path.splitext(base_name)
            output_file = os.path.join(self.output_folder, f"{file_name}_transcription.txt")
            
            with open(output_file, "w", encoding="utf-8") as f:
                text = result["text"]
                f.write(text if self.linebreaks_var.get() == "NON" else text.replace(". ", "\n"))
            
            self.log("Transcription terminée avec succès !")
            self.progress_label.config(text="Transcription terminée")
            messagebox.showinfo("Succès", f"Transcription terminée !\nFichier sauvegardé :\n{output_file}")
        except Exception as e:
            self.log(f"Erreur: {str(e)}")
            self.progress_label.config(text="Erreur lors de la transcription")
            messagebox.showerror("Erreur", str(e))
        finally:
            self.progress.stop()
            self.transcription_button.config(state="normal")
            self.cancel_button.config(state="disabled")

if __name__ == "__main__":
    root = tk.Tk()
    app = WhisperApp(root)
    root.mainloop()
