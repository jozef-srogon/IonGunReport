import os

import customtkinter as ctk
from tkinter import filedialog, messagebox
from charset_normalizer import from_path
from PIL import Image as PILImage

from models.systemName import System
from models.measurement import Measurement
from models.image import Image

from app.pdf_images import export_images_to_pdf
from app.pdf_table import export_txt_to_pdf
from app.functions import resource_path, point_in_polygon
from app.systemConfig import get_system_config

from app.version_utils import get_version
import threading
from app.update_check import check_latest

from pathlib import Path

class App(ctk.CTk):
    BG_COLOR = "#2B2B2B"   
    BG_COLOR_HOVER ="#5E5D5D"
    
    def __init__(self):
        super().__init__()

        self.configure(fg_color=self.BG_COLOR)
        self.geometry("1000x700")

        ver = get_version()
        self.title(F"IONify - v{ver}")

        self.iconbitmap(resource_path("assets/app_icon.ico"))

        self.system = []
        self.images = []
        self.import_folder_path = ""
        self.import_file_path = ""
        self.system_var = ctk.BooleanVar(value=False)  # False = Escalab, True = Nexsa
        self.ionGun_var = ctk.BooleanVar(value=False)  # MAGCIS / EX06
        self.ISS_modes = ctk.BooleanVar(value=False)   # ISS modes for Nexsa
        self.oe_access = ctk.BooleanVar(value=False)   

        self.ORIGINAL_DESIGN_WIDTH = 892
        self.ORIGINAL_DESIGN_HEIGHT = 501

        self._load_images()
        self._create_background()

        self._current_cursor = ""
        self.bg_label.bind("<Motion>", self.on_motion)
        self.bg_label.bind("<Leave>", self.on_leave)

        self._create_title_area()
        self._create_tooltip()
        self._create_buttons()
        self.after(2000, self.start_update_check)

    def start_update_check(self):
        threading.Thread(
            target=check_latest,
            kwargs={"parent": self},
            daemon=True
        ).start()

    def _load_ctk_image(self, relpath: str, size: tuple):
        p = resource_path(relpath)
        try:
            pil = PILImage.open(p)
            return ctk.CTkImage(pil, size=size)
        except Exception:
            return None
        
    def _load_images(self):
        self.bg_escalab_img = self._load_ctk_image("assets/EscalabSelected2.png", (892, 501))
        self.bg_nexsa_img   = self._load_ctk_image("assets/NexsaSelected2.png", (892, 501))
        self.icon_normal    = self._load_ctk_image("assets/info_icon_normal.png", (20, 20))
        self.icon_hover     = self._load_ctk_image("assets/hover2.png", (20, 20))

    def _create_background(self):
        kwargs = {"text": ""}
        if self.bg_escalab_img:
            kwargs["image"] = self.bg_escalab_img
        self.bg_label = ctk.CTkLabel(self, **kwargs)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        self.bg_label.bind("<Button-1>", self.on_click)
        self.bg_label.lower()

    def _create_title_area(self):
        TITLE_HEIGHT = 36
        title_frame = ctk.CTkFrame(
            self,
            fg_color=self.BG_COLOR,
            height=TITLE_HEIGHT
        )
        title_frame.pack(fill="x", pady=(5, 0))
        title_frame.pack_propagate(False)

        self.label = ctk.CTkLabel(
            title_frame,
            text="Convert to PDF",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="white",
            fg_color=self.BG_COLOR
        )
        self.label.place(relx=0.5, rely=0.5, anchor="center")

        self.info_button = ctk.CTkButton(
            title_frame,
            image=self.icon_normal,
            text="",
            width=20,
            height=20,
            fg_color=self.BG_COLOR,
            hover_color=self.BG_COLOR,
            command=lambda: None
        )
        self.info_button.place(relx=0.5, rely=0.5, anchor="w", x=55)

        self.info_button.bind("<Enter>", self._on_info_hover)
        self.info_button.bind("<Leave>", self._on_info_leave)

    def _create_tooltip(self):
        self.tooltip = ctk.CTkToplevel(self)
        self.tooltip.withdraw()
        self.tooltip.overrideredirect(True)
        self.tooltip.attributes("-topmost", True)

        tip_label = ctk.CTkLabel(
            self.tooltip,
            text=(
                "1. Choose your system type.\n"
                "2. Click “Run script”.\n"
                "3. The PDF files will be generated inside the IonGun folder.\n"
                "4. Validate and upload it to Final Test."
            ),
            font=ctk.CTkFont(size=12),
            fg_color="#3A3A3A",
            text_color="white",
            wraplength=350,
            justify="left",
            padx=10,
            pady=5
        )
        tip_label.pack()

    def _create_buttons(self):
        button_frame = ctk.CTkFrame(self, fg_color=self.BG_COLOR)
        button_frame.pack(pady=5)

        self.upload_button = ctk.CTkButton(
            button_frame,
            text="Run script",
            hover_color=self.BG_COLOR_HOVER,
            fg_color="#3A3A3A",
            command=self.import_folder,
            corner_radius=3,
            width=100
        )
        self.upload_button.pack(side="left", padx=5)

        self.open_button = ctk.CTkButton(
            button_frame,
            text="Open Folder",
            hover_color=self.BG_COLOR_HOVER,
            fg_color="#3A3A3A",
            command=self.open_folder,
            corner_radius=3,
            width=100
        )
        self.open_button.pack_forget()

        self.default_data_button = ctk.CTkButton(
            button_frame,
            text="View Defaults",
            hover_color=self.BG_COLOR_HOVER,
            fg_color="#3A3A3A",
            command=self.open_default_data,
            corner_radius=3,
            width=100
        )
        self.default_data_button.pack_forget()

    def _on_info_hover(self, event):
        self.info_button.configure(image=self.icon_hover)
        x = self.info_button.winfo_rootx() + self.info_button.winfo_width() + 6
        y = self.info_button.winfo_rooty()
        self.tooltip.geometry(f"+{x}+{y}")
        self.tooltip.deiconify()

    def _on_info_leave(self, event):
        self.info_button.configure(image=self.icon_normal)
        self.tooltip.withdraw()

    def update_background(self):
        if self.system_var.get():  # Nexsa
            self.bg_label.configure(image=self.bg_nexsa_img)
        else:  # Escalab
            self.bg_label.configure(image=self.bg_escalab_img)

    def import_folder(self):
        self.system = []
        self.images = []
        self.import_folder_path = ""
        self.ionGun_var = ctk.BooleanVar(value=False)  # MAGCIS / EX06
        self.ISS_modes = ctk.BooleanVar(value=False)   # ISS modes for Nexsa
        self.oe_access.set(False)

        try:
            default_folder = "C:/AvantageSystem/RampLogs/IonGun"
            folder_path = default_folder if os.path.isdir(default_folder) else filedialog.askdirectory(title="Select IonGun folder")
            if not folder_path:
                return
            self.import_folder_path = folder_path

            bmp_files = [f for f in os.listdir(folder_path) if f.lower().endswith(".bmp")]
            for bmp_file in bmp_files:
                full_path = os.path.join(folder_path, bmp_file)
                self.images.append(Image(bmp_file, full_path))

            if self.images:
                export_images_to_pdf(self.images, self.import_folder_path)
            
            txt_files = [f for f in os.listdir(folder_path) if f.lower().endswith(".txt")]
            for txt_file in txt_files:
                self.ionGun_var.set(False)
                self.ISS_modes.set(False)
                self.import_file_path = os.path.join(folder_path, txt_file)
                if os.path.isfile(self.import_file_path):
                    if self.process_file(self.import_file_path):
                        self.open_folder()
                        self.open_button.pack(side="left", padx=5)
                        self.default_data_button.pack(side="left", padx=5)
                else:
                    messagebox.showwarning("Warning", "Best Mode Data file not found.")

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def open_folder(self):
        try:
            if not self.import_folder_path or not os.path.isdir(self.import_folder_path):
                messagebox.showwarning("Warning", "Folder path is not valid.")
                return
            os.startfile(self.import_folder_path)
            txt_path = os.path.join(self.import_folder_path, "BestModeData_V3.pdf")
            os.startfile(txt_path)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def process_file(self, file=None):
        self.system = []
        try:
            encoding = from_path(file).best().encoding
            with open(file, "r", encoding=encoding) as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue                 
                    if line == "isolemnlyswearthatiamuptonogood" or line == "slavnostneprisahamzejsempripravenkekazdespatnosti" or line == "slavnostneprisahamzenemamzalubomnicdobre":
                        self.oe_access.set(True)
                    if line.startswith("Date"):
                        self.system = System(line)
                    else:
                        parts = line.split()
                        if len(parts) < 21:
                            continue

                        if parts[0] in ("[14]", "[20]", "[26]", "[32]") and parts[3] == "75":
                            self.ISS_modes.set(True)
                            self.ionGun_var.set(True)
                        elif parts[0] in ("[15]", "[21]", "[27]", "[33]") and parts[3] == "150":
                            self.ISS_modes.set(True)
                            self.ionGun_var.set(True)
                        elif parts[0] in ("[16]", "[22]", "[28]", "[34]") and parts[3] == "300":
                            self.ISS_modes.set(True)
                            self.ionGun_var.set(True)
                        elif parts[0] in ("[17]", "[23]", "[29]", "[35]") and parts[3] == "500":
                            self.ISS_modes.set(True)
                            self.ionGun_var.set(True)
                        elif parts[0] in  ("[18]", "[24]", "[30]", "[36]") and parts[3] == "1000":
                            self.ISS_modes.set(True)
                            self.ionGun_var.set(True)
                        elif parts[0] in  ("[19]", "[25]", "[31]", "[37]") and parts[3] == "2000":
                            self.ionGun_var.set(True)
                            self.ISS_modes.set(True)                     

                        if parts[9] != "0" and parts[12] != "-0":
                            self.ionGun_var.set(True)

                        if parts[3] == "Med":
                            self.ionGun_var.set(False)
                        if parts[20] == "ISS":
                            self.ISS_modes.set(True)
                        if parts[20] == "Cluster":
                            self.ionGun_var.set(True)
                        else:
                            pass

                        self.system.results.append(
                            Measurement(
                                date=parts[1] + " " + parts[2],
                                index=parts[0],
                                setup=parts[3],
                                ion_energy_eV=float(parts[4]),
                                ion_energy_uA=float(parts[5]),
                                electron_energy_eV=float(parts[6]),
                                electron_energy_mA=float(parts[7]),
                                fil=float(parts[8]),
                                extractor=float(parts[9]),
                                condensor=float(parts[10]),
                                drift=float(parts[11]),
                                magnet=float(parts[12]),
                                focus=float(parts[13]),
                                X_shift=float(parts[14]),
                                Y_shift=float(parts[15]),
                                ratio=float(parts[16]),
                                sample_current_work=float(parts[17]),
                                sample_current_max=float(parts[18]),
                                sample_current_aim=float(parts[19]),
                                mode=parts[20],
                                specification=parts[21] if len(parts) > 21 else ""
                            )
                        )
            
            wrong_modes = export_txt_to_pdf(self.system, self.import_folder_path, self.system_var.get(), self.ionGun_var.get(), self.ISS_modes.get(), self.oe_access.get(), file)
            if wrong_modes is None:
                return False
            elif wrong_modes != []:
                lines = ["Please check values:"]
                lines += [f"Mode {i[0]}: {i[1]} value" for i in wrong_modes]
                messagebox.showwarning("Wrong Modes", "\n".join(lines))
            else:
                pass
                
        except Exception as e:
            messagebox.showerror("Error", str(e))

        return True
    
    def open_default_data(self):
        try:
            systemType = get_system_config(self.system_var.get(), self.ionGun_var.get(), self.ISS_modes.get())["system"]
            pdf_path = resource_path(f"assets/{systemType}.pdf")

            if not os.path.isfile(pdf_path):
                messagebox.showerror("File not found", "Default values PDF could not be found.")
                return
            
            os.startfile(pdf_path)

        except Exception as e:
            messagebox.showerror("Error", f"Could not open the PDF file:\n{e}")

    def _hit_test_region(self, event):
        try:
            scaling = self._get_window_scaling()
        except AttributeError:
            scaling = ctk.ThemeManager.theme.get("scaling", 1.0)

        cur_x = event.x / scaling
        cur_y = event.y / scaling

        widget_w = event.widget.winfo_width() / scaling
        widget_h = event.widget.winfo_height() / scaling

        offset_x = (widget_w - self.ORIGINAL_DESIGN_WIDTH) / 2
        offset_y = (widget_h - self.ORIGINAL_DESIGN_HEIGHT) / 2

        if not (
            offset_x <= cur_x <= offset_x + self.ORIGINAL_DESIGN_WIDTH and
            offset_y <= cur_y <= offset_y + self.ORIGINAL_DESIGN_HEIGHT
        ):
            return None

        virtual_x = cur_x - offset_x
        virtual_y = cur_y - offset_y

        poly_left = [
            (0, self.ORIGINAL_DESIGN_HEIGHT),
            (369, self.ORIGINAL_DESIGN_HEIGHT),
            (468, 0),
            (0, 0),
        ]

        poly_right = [
            (369, self.ORIGINAL_DESIGN_HEIGHT),
            (self.ORIGINAL_DESIGN_WIDTH, self.ORIGINAL_DESIGN_HEIGHT),
            (self.ORIGINAL_DESIGN_WIDTH, 0),
            (468, 0),
        ]

        if point_in_polygon(virtual_x, virtual_y, poly_left):
            return "left"

        if point_in_polygon(virtual_x, virtual_y, poly_right):
            return "right"

        return None
    
    def on_click(self, event):
        region = self._hit_test_region(event)

        if region == "left":
            self.system_var.set(False)
            self.bg_label.configure(image=self.bg_escalab_img)

        elif region == "right":
            self.system_var.set(True)
            self.bg_label.configure(image=self.bg_nexsa_img)

    def on_motion(self, event):
        region = self._hit_test_region(event)

        if region in ("left", "right"):
            self._set_cursor("hand2")
        else:
            self._set_cursor("arrow")

    def on_leave(self, event):
        self._set_cursor("arrow")

    def _set_cursor(self, cursor_name):
        if cursor_name == self._current_cursor:
            return
        try:
            self.bg_label.configure(cursor=cursor_name)
        except Exception:
            pass
        self._current_cursor = cursor_name
