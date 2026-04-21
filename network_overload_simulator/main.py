import tkinter as tk
from tkinter import messagebox

import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class NetworkSimulationApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Network Congestion Simulator")
        self.geometry("1400x850")
        self.minsize(1200, 750)

        # -----------------------------
        # default values for parameters
        # -----------------------------
        self.default_params = {
            "arrival_rate": "0.5",
            "processing_time": "5",
            "max_queue": "5",
            "simulation_time": "100",
            "runs_per_rate": "3",
            "rates_list": "0.25, 0.5, 0.75, 1, 2"
        }

        # variables for entry fields
        self.param_vars = {
            key: ctk.StringVar(value=value)
            for key, value in self.default_params.items()
        }

        # values that were actually applied
        self.applied_config = None

        # variables for results block
        self.result_vars = {
            "average_delay": ctk.StringVar(value="-"),
            "loss_rate": ctk.StringVar(value="-"),
            "average_queue": ctk.StringVar(value="-"),
            "total_packets": ctk.StringVar(value="-"),
            "processed_packets": ctk.StringVar(value="-"),
            "lost_packets": ctk.StringVar(value="-"),
        }

        self._configure_grid()
        self._create_menu()
        self._create_header()
        self._create_sidebar()
        self._create_center_area()
        self._create_parameter_panel()

        self.log_event("Application started")

    def _configure_grid(self):
        self.grid_columnconfigure(0, weight=0)  # sidebar
        self.grid_columnconfigure(1, weight=1)  # center
        self.grid_rowconfigure(0, weight=0)     # header
        self.grid_rowconfigure(1, weight=1)     # main content
        self.grid_rowconfigure(2, weight=0)     # bottom parameters

    def _create_menu(self):
        menubar = tk.Menu(self)

        about_menu = tk.Menu(menubar, tearoff=0)
        about_menu.add_command(label="About program", command=self.show_about)

        menubar.add_cascade(label="About", menu=about_menu)
        self.config(menu=menubar)

    def _create_header(self):
        header_frame = ctk.CTkFrame(self, corner_radius=0)
        header_frame.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=0, pady=0)

        title_label = ctk.CTkLabel(
            header_frame,
            text="Network Congestion Simulator",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title_label.pack(pady=(16, 4))

        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="Simulation and visualization of packet delay, loss and queue dynamics",
            font=ctk.CTkFont(size=14)
        )
        subtitle_label.pack(pady=(0, 12))

    def _create_sidebar(self):
        self.sidebar_frame = ctk.CTkFrame(self, width=270)
        self.sidebar_frame.grid(row=1, column=0, sticky="nsew", padx=(15, 8), pady=(15, 8))
        self.sidebar_frame.grid_propagate(False)

        button_title = ctk.CTkLabel(
            self.sidebar_frame,
            text="Control panel",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        button_title.pack(pady=(15, 10))

        button_width = 220
        button_height = 40

        self.run_single_button = ctk.CTkButton(
            self.sidebar_frame,
            text="Run (1 simulation)",
            width=button_width,
            height=button_height,
            command=self.run_single_simulation
        )
        self.run_single_button.pack(pady=6)

        self.run_series_button = ctk.CTkButton(
            self.sidebar_frame,
            text="Run (series of simulations)",
            width=button_width,
            height=button_height,
            command=self.run_series_simulation
        )
        self.run_series_button.pack(pady=6)

        self.apply_button = ctk.CTkButton(
            self.sidebar_frame,
            text="Apply",
            width=button_width,
            height=button_height,
            command=self.apply_parameters
        )
        self.apply_button.pack(pady=6)

        self.reset_button = ctk.CTkButton(
            self.sidebar_frame,
            text="Reset",
            width=button_width,
            height=button_height,
            command=self.reset_parameters
        )
        self.reset_button.pack(pady=6)

        self.clear_button = ctk.CTkButton(
            self.sidebar_frame,
            text="Clear",
            width=button_width,
            height=button_height,
            command=self.clear_parameters
        )
        self.clear_button.pack(pady=6)

        self.save_button = ctk.CTkButton(
            self.sidebar_frame,
            text="Save (chart)",
            width=button_width,
            height=button_height,
            command=self.save_chart
        )
        self.save_button.pack(pady=6)

        self.export_button = ctk.CTkButton(
            self.sidebar_frame,
            text="Export",
            width=button_width,
            height=button_height,
            command=self.export_results
        )
        self.export_button.pack(pady=6)

        # applied parameters block
        applied_frame = ctk.CTkFrame(self.sidebar_frame)
        applied_frame.pack(fill="both", expand=True, padx=15, pady=(20, 10))

        applied_title = ctk.CTkLabel(
            applied_frame,
            text="Applied parameters",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        applied_title.pack(pady=(10, 5))

        self.applied_textbox = ctk.CTkTextbox(applied_frame, height=220, wrap="word")
        self.applied_textbox.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.applied_textbox.insert("0.0", "No parameters applied yet.")
        self.applied_textbox.configure(state="disabled")

        self.status_label = ctk.CTkLabel(
            self.sidebar_frame,
            text="Status: waiting for input",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(pady=(0, 12))

    def _create_center_area(self):
        self.center_frame = ctk.CTkFrame(self)
        self.center_frame.grid(row=1, column=1, sticky="nsew", padx=(8, 15), pady=(15, 8))
        self.center_frame.grid_rowconfigure(0, weight=1)
        self.center_frame.grid_columnconfigure(0, weight=1)

        self.tabview = ctk.CTkTabview(self.center_frame)
        self.tabview.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.tabview.add("Dashboard")
        self.tabview.add("Results")
        self.tabview.add("Event log")

        self._create_dashboard_tab()
        self._create_results_tab()
        self._create_event_log_tab()

    def _create_dashboard_tab(self):
        dashboard_tab = self.tabview.tab("Dashboard")
        dashboard_tab.grid_rowconfigure(0, weight=1)
        dashboard_tab.grid_columnconfigure(0, weight=1)

        self.figure = Figure(figsize=(10, 4), dpi=100)
        self.ax1 = self.figure.add_subplot(131)
        self.ax2 = self.figure.add_subplot(132)
        self.ax3 = self.figure.add_subplot(133)

        self.ax1.set_title("Average delay")
        self.ax2.set_title("Loss rate")
        self.ax3.set_title("Average queue")

        self.ax1.set_xlabel("Rate")
        self.ax2.set_xlabel("Rate")
        self.ax3.set_xlabel("Rate")

        self.ax1.set_ylabel("Delay")
        self.ax2.set_ylabel("Loss")
        self.ax3.set_ylabel("Queue")

        self.ax1.grid(True, linestyle="--", alpha=0.5)
        self.ax2.grid(True, linestyle="--", alpha=0.5)
        self.ax3.grid(True, linestyle="--", alpha=0.5)

        self.figure.tight_layout()

        self.canvas = FigureCanvasTkAgg(self.figure, master=dashboard_tab)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

    def _create_results_tab(self):
        results_tab = self.tabview.tab("Results")
        results_tab.grid_columnconfigure((0, 1, 2), weight=1)

        cards = [
            ("Average delay", "average_delay"),
            ("Loss rate", "loss_rate"),
            ("Average queue", "average_queue"),
            ("Total packets", "total_packets"),
            ("Processed packets", "processed_packets"),
            ("Lost packets", "lost_packets"),
        ]

        for index, (title, key) in enumerate(cards):
            row = index // 3
            col = index % 3

            card = ctk.CTkFrame(results_tab)
            card.grid(row=row, column=col, sticky="nsew", padx=12, pady=12)

            title_label = ctk.CTkLabel(
                card,
                text=title,
                font=ctk.CTkFont(size=15, weight="bold")
            )
            title_label.pack(pady=(18, 8))

            value_label = ctk.CTkLabel(
                card,
                textvariable=self.result_vars[key],
                font=ctk.CTkFont(size=24)
            )
            value_label.pack(pady=(0, 18))

    def _create_event_log_tab(self):
        log_tab = self.tabview.tab("Event log")
        log_tab.grid_rowconfigure(0, weight=1)
        log_tab.grid_columnconfigure(0, weight=1)

        self.log_textbox = ctk.CTkTextbox(log_tab, wrap="word")
        self.log_textbox.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.log_textbox.insert("0.0", "Event log initialized...\n")
        self.log_textbox.configure(state="disabled")

    def _create_parameter_panel(self):
        self.params_frame = ctk.CTkFrame(self)
        self.params_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=15, pady=(8, 15))

        title = ctk.CTkLabel(
            self.params_frame,
            text="Simulation parameters",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title.grid(row=0, column=0, columnspan=6, padx=12, pady=(12, 10), sticky="w")

        param_titles = [
            ("Arrival rate", "arrival_rate"),
            ("Processing time", "processing_time"),
            ("Max queue", "max_queue"),
            ("Simulation time", "simulation_time"),
            ("Runs per rate", "runs_per_rate"),
            ("Rates list", "rates_list"),
        ]

        for col, (label_text, key) in enumerate(param_titles):
            self.params_frame.grid_columnconfigure(col, weight=1)

            field_frame = ctk.CTkFrame(self.params_frame)
            field_frame.grid(row=1, column=col, sticky="ew", padx=8, pady=(0, 12))

            label = ctk.CTkLabel(
                field_frame,
                text=label_text,
                font=ctk.CTkFont(size=13, weight="bold")
            )
            label.pack(anchor="w", padx=10, pady=(8, 4))

            entry = ctk.CTkEntry(field_frame, textvariable=self.param_vars[key], height=34)
            entry.pack(fill="x", padx=10, pady=(0, 10))

    # -----------------------------
    # utility methods
    # -----------------------------
    def show_about(self):
        messagebox.showinfo(
            "About",
            "Network Congestion Simulator\n\n"
            "GUI skeleton for a course project.\n"
            "CustomTkinter + Matplotlib interface."
        )

    def log_event(self, message):
        self.log_textbox.configure(state="normal")
        self.log_textbox.insert("end", f"{message}\n")
        self.log_textbox.see("end")
        self.log_textbox.configure(state="disabled")

    def set_status(self, text):
        self.status_label.configure(text=f"Status: {text}")

    def update_applied_parameters_box(self):
        if not self.applied_config:
            text = "No parameters applied yet."
        else:
            text = (
                f"Arrival rate: {self.applied_config['arrival_rate']}\n"
                f"Processing time: {self.applied_config['processing_time']}\n"
                f"Max queue: {self.applied_config['max_queue']}\n"
                f"Simulation time: {self.applied_config['simulation_time']}\n"
                f"Runs per rate: {self.applied_config['runs_per_rate']}\n"
                f"Rates list: {self.applied_config['rates_list']}\n"
            )

        self.applied_textbox.configure(state="normal")
        self.applied_textbox.delete("0.0", "end")
        self.applied_textbox.insert("0.0", text)
        self.applied_textbox.configure(state="disabled")

    # -----------------------------
    # button actions (skeleton)
    # -----------------------------
    def apply_parameters(self):
        self.applied_config = {
            key: var.get()
            for key, var in self.param_vars.items()
        }
        self.update_applied_parameters_box()
        self.set_status("parameters applied")
        self.log_event("Parameters applied")

    def reset_parameters(self):
        for key, value in self.default_params.items():
            self.param_vars[key].set(value)

        self.set_status("parameters reset to defaults")
        self.log_event("Parameters reset to default values")

    def clear_parameters(self):
        for var in self.param_vars.values():
            var.set("")

        self.set_status("parameter fields cleared")
        self.log_event("Parameter fields cleared")

    def run_single_simulation(self):
        if not self.applied_config:
            messagebox.showwarning("Warning", "Please apply parameters first.")
            return

        self.set_status("single simulation started")
        self.log_event("Single simulation started")

        # TODO:
        # here you will connect your existing simulation logic
        # and update result_vars with real values

        self.result_vars["average_delay"].set("12.40")
        self.result_vars["loss_rate"].set("8.20%")
        self.result_vars["average_queue"].set("3.15")
        self.result_vars["total_packets"].set("150")
        self.result_vars["processed_packets"].set("138")
        self.result_vars["lost_packets"].set("12")

        self.set_status("single simulation finished")
        self.log_event("Single simulation finished")

    def run_series_simulation(self):
        if not self.applied_config:
            messagebox.showwarning("Warning", "Please apply parameters first.")
            return

        self.set_status("series simulation started")
        self.log_event("Series of simulations started")

        # TODO:
        # here you will connect batch simulation logic
        # and refresh matplotlib charts with real data

        self.ax1.clear()
        self.ax2.clear()
        self.ax3.clear()

        rates = [0.25, 0.5, 0.75, 1, 2]
        delays = [2.1, 3.0, 4.2, 6.8, 12.4]
        losses = [0.0, 0.01, 0.03, 0.08, 0.16]
        queues = [0.8, 1.2, 1.7, 2.4, 3.1]

        self.ax1.plot(rates, delays, marker="o")
        self.ax2.plot(rates, losses, marker="o")
        self.ax3.plot(rates, queues, marker="o")

        self.ax1.set_title("Average delay")
        self.ax2.set_title("Loss rate")
        self.ax3.set_title("Average queue")

        self.ax1.set_xlabel("Rate")
        self.ax2.set_xlabel("Rate")
        self.ax3.set_xlabel("Rate")

        self.ax1.set_ylabel("Delay")
        self.ax2.set_ylabel("Loss")
        self.ax3.set_ylabel("Queue")

        self.ax1.grid(True, linestyle="--", alpha=0.5)
        self.ax2.grid(True, linestyle="--", alpha=0.5)
        self.ax3.grid(True, linestyle="--", alpha=0.5)

        self.figure.tight_layout()
        self.canvas.draw()

        self.set_status("series simulation finished")
        self.log_event("Series of simulations finished")

    def save_chart(self):
        self.log_event("Save chart clicked")
        self.set_status("save chart action triggered")
        messagebox.showinfo("Info", "Chart save action placeholder.")

    def export_results(self):
        self.log_event("Export clicked")
        self.set_status("export action triggered")
        messagebox.showinfo("Info", "Export action placeholder.")


if __name__ == "__main__":
    app = NetworkSimulationApp()
    app.mainloop()