import os
from dotenv import load_dotenv
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
from instagrapi import Client

from main import ContentQueue, CaptionManager, BackupBot

# Load environment variables from .env
load_dotenv()
IG_USERNAME = "officialmarionormil"
IG_PASSWORD = "Bk10ngh301!@$196179"

class PostingBot:
    def __init__(self, session_file="session.json"):
        self.username = IG_USERNAME
        self.password = IG_PASSWORD
        self.session_file = session_file
        self.client = Client()
        self._login()

    def _login(self):
        if os.path.exists(self.session_file):
            try:
                self.client.load_settings(self.session_file)
            except Exception:
                pass
        try:
            self.client.login(self.username, self.password)
            self.client.dump_settings(self.session_file)
        except Exception as e:
            messagebox.showerror("Login Error", f"Instagram login failed: {e}")
            raise

    def post(self, media_path, caption):
        try:
            if media_path.lower().endswith(('.jpg', '.jpeg', '.png')):
                self.client.photo_upload(media_path, caption)
            elif media_path.lower().endswith(('.mp4', '.mov')):
                self.client.video_upload(media_path, caption)
            else:
                raise ValueError("Unsupported media format.")
            return True
        except Exception as e:
            messagebox.showerror("Post Error", f"Failed to post: {e}")
            return False

class SMSAControlPanel(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SMSA Control Panel")
        self.geometry("1000x700")
        self.queue = ContentQueue()
        self.captions = CaptionManager()
        self.poster = PostingBot()
        self.backup = BackupBot()
        self._build_tabs()

    def _build_tabs(self):
        tab_control = ttk.Notebook(self)
        self.dashboard_tab = ttk.Frame(tab_control)
        self.upload_tab = ttk.Frame(tab_control)
        self.archive_tab = ttk.Frame(tab_control)
        self.logs_tab = ttk.Frame(tab_control)
        self.settings_tab = ttk.Frame(tab_control)

        tab_control.add(self.dashboard_tab, text='Dashboard')
        tab_control.add(self.upload_tab, text='Content Upload')
        tab_control.add(self.archive_tab, text='Archive Viewer')
        tab_control.add(self.logs_tab, text='Logs')
        tab_control.add(self.settings_tab, text='Settings')
        tab_control.pack(expand=1, fill='both')

        self._build_dashboard()
        self._build_upload()
        # Archive, Logs, Settings: stubs for now

    def _build_dashboard(self):
        # Preview next content
        tk.Label(self.dashboard_tab, text="Next Content Preview", font=("Arial", 14)).pack(pady=10)
        self.preview_canvas = tk.Canvas(self.dashboard_tab, width=400, height=400, bg='gray90')
        self.preview_canvas.pack()
        self._update_preview()

        # Caption preview
        self.caption_var = tk.StringVar()
        tk.Label(self.dashboard_tab, text="Random Caption:").pack(pady=5)
        self.caption_entry = tk.Entry(self.dashboard_tab, textvariable=self.caption_var, width=80)
        self.caption_entry.pack(pady=5)
        self._update_caption()

        # Action buttons
        btn_frame = tk.Frame(self.dashboard_tab)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="POST", command=self._post_content, bg="#4CAF50", fg="white", width=12).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="BACKUP", command=self._backup_content, bg="#2196F3", fg="white", width=12).pack(side=tk.LEFT, padx=5)
        tk.Button(
            btn_frame,
            text="SCHEDULE",
            command=self._schedule_post,
            bg="#FF9800",
            fg="white",
            width=12
        ).pack(side=tk.LEFT, padx=5)

    def _build_upload(self):
        tk.Label(self.upload_tab, text="Add Content to Queue", font=("Arial", 14)).pack(pady=10)
        tk.Button(self.upload_tab, text="Add Files", command=self._add_files).pack(pady=5)
        self.queue_listbox = tk.Listbox(self.upload_tab, width=80, height=20)
        self.queue_listbox.pack(pady=10)
        self._refresh_queue_list()

    def _update_preview(self):
        media = self.queue.get_next_content()
        self.preview_canvas.delete("all")
        if media and media.lower().endswith(('.jpg', '.jpeg', '.png')):
            img = Image.open(media)
            img.thumbnail((400, 400))
            self.imgtk = ImageTk.PhotoImage(img)
            self.preview_canvas.create_image(200, 200, image=self.imgtk)
        else:
            self.preview_canvas.create_text(200, 200, text="No image to preview", font=("Arial", 16))

    def _update_caption(self):
        self.caption_var.set(self.captions.get_random_caption())

    def _post_content(self):
        media = self.queue.get_next_content()
        caption = self.caption_var.get()
        if not media:
            messagebox.showwarning("No Content", "No content to post.")
            return
        if self.poster.post(media, caption):
            self.queue.mark_as_posted(media)
            messagebox.showinfo("Success", f"Posted: {os.path.basename(media)}")
            self._update_preview()
            self._refresh_queue_list()
            self._update_caption()
        else:
            messagebox.showerror("Error", "Failed to post content.")

    def _backup_content(self):
        self.backup.backup_all()
        messagebox.showinfo("Backup", "Backup complete.")

    def _add_files(self):
        files = filedialog.askopenfilenames(
            title="Select Media Files",
            filetypes=[("Media Files", "*.jpg *.jpeg *.png *.mp4 *.mov")]
        )
        for f in files:
            shutil.copy2(f, self.queue.queue_dir)
        self._refresh_queue_list()
        self._update_preview()

    def _refresh_queue_list(self):
        self.queue_listbox.delete(0, tk.END)
        files = sorted([
            f for f in os.listdir(self.queue.queue_dir)
            if f.lower().endswith(self.queue.allowed_ext)
        ])
        for f in files:
            self.queue_listbox.insert(tk.END, f)

if __name__ == "__main__":
    app = SMSAControlPanel()
    app.mainloop()