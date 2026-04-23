import csv
import tkinter as tk
from tkinter import filedialog, messagebox

import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from pathlib import Path

from simulation import run_series_simulation as backend_run_series_simulation
from simulation import run_single_simulation as backend_run_single_simulation


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class NetworkSimulationApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Network Congestion Simulator")
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()

        self.window_w = int(screen_w * 0.9)
        self.window_h = int(screen_h * 0.85)

        self.geometry(f"{self.window_w}x{self.window_h}")
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
        self.last_single_result = None
        self.last_series_result = None
        self.last_run_type = None

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
        self._create_applied_parameters_panel()
        self._create_center_area()
        self._create_parameter_panel()

        self.log_event("Application started")

    def _configure_grid(self):
        self.grid_columnconfigure(0, weight=0)  # sidebar
        self.grid_columnconfigure(1, weight=0)  # applied parameters panel
        self.grid_columnconfigure(2, weight=1)  # center
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
        header_frame.grid(row=0, column=0, columnspan=3, sticky="nsew", padx=0, pady=0)

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
        self.sidebar_width = max(230, int(self.window_w * 0.18))
        self.sidebar_frame = ctk.CTkFrame(self, width=self.sidebar_width)
        self.sidebar_frame.grid(row=1, column=0, sticky="nsew", padx=(15, 8), pady=(15, 8))
        self.sidebar_frame.grid_propagate(False)

        button_title = ctk.CTkLabel(
            self.sidebar_frame,
            text="Control panel",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        button_title.pack(pady=(15, 10))

        button_width = int(self.sidebar_width * 0.82)
        button_height = max(34, int(self.window_h * 0.045))

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

        self.status_label = ctk.CTkLabel(
            self.sidebar_frame,
            text="Status: waiting for input",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(pady=(0, 12))

    def _create_applied_parameters_panel(self):
        self.applied_panel_width = max(240, int(self.window_w * 0.20))
        self.applied_panel_frame = ctk.CTkFrame(self, width=self.applied_panel_width)
        self.applied_panel_frame.grid(
            row=1, column=1, sticky="nsew", padx=(0, 8), pady=(15, 8)
        )
        self.applied_panel_frame.grid_propagate(False)
        self.applied_panel_frame.grid_rowconfigure(1, weight=1)
        self.applied_panel_frame.grid_columnconfigure(0, weight=1)

        applied_title = ctk.CTkLabel(
            self.applied_panel_frame,
            text="Applied parameters",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        applied_title.grid(row=0, column=0, sticky="w", padx=12, pady=(12, 8))

        self.applied_textbox = ctk.CTkTextbox(self.applied_panel_frame, wrap="word")
        self.applied_textbox.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.applied_textbox.insert("0.0", "No parameters applied yet.")
        self.applied_textbox.configure(state="disabled")

    def _create_center_area(self):
        self.center_frame = ctk.CTkFrame(self)
        self.center_frame.grid(row=1, column=2, sticky="nsew", padx=(8, 15), pady=(15, 8))
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
        self.params_frame.grid(row=2, column=0, columnspan=3, sticky="nsew", padx=15, pady=(8, 15))

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

    def _parse_applied_config(self):
        if not self.applied_config:
            raise ValueError("Please apply parameters first.")

        try:
            arrival_rate = float(self.applied_config["arrival_rate"])
            processing_time = float(self.applied_config["processing_time"])
            max_queue = int(self.applied_config["max_queue"])
            simulation_time = float(self.applied_config["simulation_time"])
            runs_per_rate = int(self.applied_config["runs_per_rate"])
            rates_list = [
                float(value.strip())
                for value in self.applied_config["rates_list"].split(",")
                if value.strip()
            ]
        except (ValueError, TypeError, KeyError) as error:
            raise ValueError("Invalid parameter format. Check all input fields.") from error

        if arrival_rate <= 0:
            raise ValueError("Arrival rate must be positive.")
        if processing_time <= 0:
            raise ValueError("Processing time must be positive.")
        if max_queue < 0:
            raise ValueError("Max queue must be non-negative.")
        if simulation_time <= 0:
            raise ValueError("Simulation time must be positive.")
        if runs_per_rate <= 0:
            raise ValueError("Runs per rate must be a positive integer.")
        if not rates_list:
            raise ValueError("Rates list cannot be empty.")
        if any(rate <= 0 for rate in rates_list):
            raise ValueError("All values in rates list must be positive.")

        parsed_config = {
            "arrival_rate": arrival_rate,
            "processing_time": processing_time,
            "max_queue": max_queue,
            "simulation_time": simulation_time,
            "runs_per_rate": runs_per_rate,
            "rates_list": rates_list,
        }
        self.log_event(f"Configuration parsed: {parsed_config}")
        return parsed_config

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
        try:
            config = self._parse_applied_config()
            result = backend_run_single_simulation(config, logger=self.log_event)

            self.result_vars["average_delay"].set(f"{result['average_delay']:.2f}")
            self.result_vars["loss_rate"].set(f"{result['loss_rate'] * 100:.2f}%")
            self.result_vars["average_queue"].set(f"{result['average_queue']:.2f}")
            self.result_vars["total_packets"].set(str(result["total_packets"]))
            self.result_vars["processed_packets"].set(str(result["processed_packets"]))
            self.result_vars["lost_packets"].set(str(result["lost_packets"]))
            self.last_single_result = result
            self.last_series_result = None
            self.last_run_type = "single"

            self.set_status("single simulation finished")
            self.log_event("Single simulation finished")
        except Exception as error:
            self.set_status("single simulation failed")
            self.log_event(f"Single simulation error: {error}")
            messagebox.showerror("Simulation error", str(error))

    def run_series_simulation(self):
        if not self.applied_config:
            messagebox.showwarning("Warning", "Please apply parameters first.")
            return

        self.set_status("series simulation started")
        self.log_event("Series of simulations started")
        try:
            config = self._parse_applied_config()
            result = backend_run_series_simulation(config, logger=self.log_event)

            self.ax1.clear()
            self.ax2.clear()
            self.ax3.clear()

            rates = result["rates"]
            delays = result["delays"]
            losses = result["losses"]
            queues = result["queues"]
            self.last_series_result = result
            self.last_run_type = "series"

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
        except Exception as error:
            self.set_status("series simulation failed")
            self.log_event(f"Series simulation error: {error}")
            messagebox.showerror("Simulation error", str(error))

    def save_chart(self):
        self.log_event("Save chart clicked")
        if self.last_series_result is None:
            messagebox.showwarning(
                "Warning",
                "Run series simulation first to generate charts for export.",
            )
            self.log_event("Chart save aborted: no series data")
            return

        target_path = filedialog.asksaveasfilename(
            title="Save chart images",
            defaultextension=".png",
            filetypes=[("PNG image", "*.png")],
            initialfile="network_simulation_chart.png",
        )
        if not target_path:
            self.log_event("Chart save cancelled by user")
            return

        selected = Path(target_path)
        base_name = selected.stem
        save_dir = selected.parent

        chart_definitions = [
            ("average_delay", "Average delay", "Rate", "Delay", self.last_series_result["rates"], self.last_series_result["delays"]),
            ("loss_rate", "Loss rate", "Rate", "Loss", self.last_series_result["rates"], self.last_series_result["losses"]),
            ("average_queue", "Average queue", "Rate", "Queue", self.last_series_result["rates"], self.last_series_result["queues"]),
        ]

        saved_paths = []
        for suffix, title, x_label, y_label, x_values, y_values in chart_definitions:
            chart_figure = Figure(figsize=(6, 4), dpi=120)
            chart_axis = chart_figure.add_subplot(111)
            chart_axis.plot(x_values, y_values, marker="o")
            chart_axis.set_title(title)
            chart_axis.set_xlabel(x_label)
            chart_axis.set_ylabel(y_label)
            chart_axis.grid(True, linestyle="--", alpha=0.5)
            chart_figure.tight_layout()

            chart_path = save_dir / f"{base_name}_{suffix}.png"
            chart_figure.savefig(chart_path)
            saved_paths.append(str(chart_path))

        self.set_status("chart saved")
        self.log_event(f"Chart saved to {save_dir}")
        messagebox.showinfo("Saved", "Charts saved:\n" + "\n".join(saved_paths))

    def export_results(self):
        self.log_event("Export clicked")
        if not self.applied_config:
            messagebox.showwarning("Warning", "Apply parameters before export.")
            self.log_event("Export aborted: parameters are not applied")
            return

        if self.last_single_result is None and self.last_series_result is None:
            messagebox.showwarning("Warning", "Run simulation before export.")
            self.log_event("Export aborted: no simulation results")
            return

        target_path = filedialog.asksaveasfilename(
            title="Export simulation results",
            defaultextension=".csv",
            filetypes=[("CSV file", "*.csv")],
            initialfile="network_simulation_export.csv",
        )
        if not target_path:
            self.log_event("Export cancelled by user")
            return

        export_rows = []
        export_rows.append(["section", "key", "value"])
        export_rows.append(["applied_parameters", "arrival_rate", self.applied_config["arrival_rate"]])
        export_rows.append(["applied_parameters", "processing_time", self.applied_config["processing_time"]])
        export_rows.append(["applied_parameters", "max_queue", self.applied_config["max_queue"]])
        export_rows.append(["applied_parameters", "simulation_time", self.applied_config["simulation_time"]])
        export_rows.append(["applied_parameters", "runs_per_rate", self.applied_config["runs_per_rate"]])
        export_rows.append(["applied_parameters", "rates_list", self.applied_config["rates_list"]])

        if self.last_single_result is not None:
            export_rows.append(["single_run_results", "average_delay", f"{self.last_single_result['average_delay']:.6f}"])
            export_rows.append(["single_run_results", "loss_rate", f"{self.last_single_result['loss_rate']:.6f}"])
            export_rows.append(["single_run_results", "average_queue", f"{self.last_single_result['average_queue']:.6f}"])
            export_rows.append(["single_run_results", "total_packets", self.last_single_result["total_packets"]])
            export_rows.append(["single_run_results", "processed_packets", self.last_single_result["processed_packets"]])
            export_rows.append(["single_run_results", "lost_packets", self.last_single_result["lost_packets"]])

        if self.last_series_result is not None:
            export_rows.append(["series_run_results", "rates_array", ",".join(map(str, self.last_series_result["rates"]))])
            export_rows.append(["series_run_results", "delays_array", ",".join(map(str, self.last_series_result["delays"]))])
            export_rows.append(["series_run_results", "losses_array", ",".join(map(str, self.last_series_result["losses"]))])
            export_rows.append(["series_run_results", "queues_array", ",".join(map(str, self.last_series_result["queues"]))])

        with open(target_path, "w", newline="", encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerows(export_rows)

        self.set_status("results exported")
        self.log_event(f"Results exported to {target_path}")
        messagebox.showinfo("Saved", f"Results exported to:\n{target_path}")


if __name__ == "__main__":
    app = NetworkSimulationApp()
    app.mainloop()