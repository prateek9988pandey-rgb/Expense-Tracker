
import tkinter as tk
from tkinter import ttk, messagebox
import csv
import os
from datetime import datetime
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

FILENAME = "expenses.csv"

class BudgetTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Budget Buddy V5.0 - Robust Indian Edition")
        self.root.geometry("700x650")

        # Error Handling: Check file permissions immediately
        if not self.initialize_file():
            self.root.destroy()
            return

        # --- UI SECTION 1: INPUTS ---
        input_frame = ttk.LabelFrame(root, text="Add New Expense")
        input_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(input_frame, text="Category:").grid(row=0, column=0, padx=5, pady=5)
        self.category_var = tk.StringVar()
        self.category_entry = ttk.Combobox(input_frame, textvariable=self.category_var, 
            values=["Food", "Travel", "Bills", "Shopping", "Health", "Other"], state="readonly")
        self.category_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="Amount (₹):").grid(row=0, column=2, padx=5, pady=5)
        self.amount_var = tk.DoubleVar()
        self.amount_entry = ttk.Entry(input_frame, textvariable=self.amount_var)
        self.amount_entry.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(input_frame, text="Description:").grid(row=1, column=0, padx=5, pady=5)
        self.desc_var = tk.StringVar()
        self.desc_entry = ttk.Entry(input_frame, textvariable=self.desc_var, width=50)
        self.desc_entry.grid(row=1, column=1, columnspan=3, padx=5, pady=5)

        ttk.Button(input_frame, text="Save Expense", command=self.add_expense).grid(row=0, column=4, rowspan=2, padx=10)

        # --- UI SECTION 2: DATA TABLE ---
        tree_frame = ttk.Frame(root)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("Date", "Category", "Amount", "Description")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)

        # --- UI SECTION 3: TOOLS ---
        action_frame = ttk.LabelFrame(root, text="Tools")
        action_frame.pack(fill="x", padx=10, pady=10)

        ttk.Button(action_frame, text="🗑️ Delete Selected", command=self.delete_expense).pack(side="left", padx=10, pady=10)
        ttk.Button(action_frame, text="📊 Monthly Report", command=self.generate_monthly_report).pack(side="left", padx=10, pady=10)
        ttk.Button(action_frame, text="🥧 Category Report", command=self.generate_category_report).pack(side="left", padx=10, pady=10)
        ttk.Button(action_frame, text="📈 Visualize Categories", command=self.visualize_categories).pack(side="left", padx=10, pady=10)
        ttk.Button(action_frame, text="🔄 Refresh Data", command=self.load_data).pack(side="left", padx=10, pady=10)

        self.total_label = ttk.Label(action_frame, text="Total: ₹0.00", font=("Arial", 12, "bold"))
        self.total_label.pack(side="right", padx=20)

        self.load_data()

    def initialize_file(self):
        try:
            if not os.path.exists(FILENAME):
                with open(FILENAME, mode='w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow(["Date", "Category", "Amount", "Description"])
            return True
        except PermissionError:
            messagebox.showerror("CRITICAL ERROR", f"Cannot access '{FILENAME}'.\n\nIs the file open in Excel? Please close it and restart the app.")
            return False
        except Exception as e:
            messagebox.showerror("Error", f"System Error: {e}")
            return False

    def add_expense(self):
        category = self.category_var.get()
        description = self.desc_var.get()
        if not category:
            messagebox.showwarning("Input Error", "Please select a Category.")
            return
        try:
            amount = float(self.amount_var.get())
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Input Error", "Amount must be a positive number (e.g., 50 or 100.50).")
            return
        date = datetime.now().strftime("%Y-%m-%d")
        try:
            with open(FILENAME, mode='a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow([date, category, amount, description])
            self.category_entry.set('')
            self.amount_var.set(0.0)
            self.desc_var.set('')
            self.load_data()
            messagebox.showinfo("Success", "Expense Saved!")
        except PermissionError:
            messagebox.showerror("File Locked", "Could not save! Please close the CSV file if it is open in Excel.")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")

    def load_data(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        total = 0.0
        try:
            if os.path.exists(FILENAME):
                with open(FILENAME, mode='r', encoding='utf-8') as file:
                    reader = csv.reader(file)
                    try:
                        next(reader) # Skip header
                    except StopIteration:
                        pass
                    for row in reader:
                        if row and len(row) == 4:
                            try:
                                amount_val = float(row[2])
                                display_row = [row[0], row[1], f"₹{row[2]}", row[3]]
                                self.tree.insert("", "end", values=display_row)
                                total += amount_val
                            except ValueError:
                                continue
        except PermissionError:
            messagebox.showerror("Error", "Cannot read data. Close the CSV file!")
            return
        except Exception as e:
            messagebox.showerror("Error", f"Could not load data: {e}")
            return
        self.total_label.config(text=f"Total: ₹{total:.2f}")

    def delete_expense(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please click on a row to delete it.")
            return
        confirm = messagebox.askyesno("Confirm", "Are you sure you want to delete this record?")
        if not confirm:
            return
        try:
            selected_values = self.tree.item(selected_item)['values']
            amount_str = str(selected_values[2]).replace("₹", "")
            with open(FILENAME, mode='r', encoding='utf-8') as file:
                reader = csv.reader(file)
                all_rows = list(reader)
            new_rows = [all_rows[0]]
            deleted = False
            for row in all_rows[1:]:
                if not deleted and len(row) >= 4 and \
                    row[0] == str(selected_values[0]) and \
                    float(row[2]) == float(amount_str) and \
                    row[3] == str(selected_values[3]):
                    deleted = True 
                else:
                    new_rows.append(row)
            with open(FILENAME, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerows(new_rows)
            self.load_data()
            messagebox.showinfo("Success", "Record Deleted.")
        except PermissionError:
            messagebox.showerror("File Locked", "Cannot delete! Please close the CSV file.")
        except Exception as e:
            messagebox.showerror("Error", f"Delete failed: {e}")

    def generate_monthly_report(self):
        totals = {} 
        try:
            if os.path.exists(FILENAME):
                with open(FILENAME, mode='r', encoding='utf-8') as file:
                    reader = csv.reader(file)
                    next(reader)
                    for row in reader:
                        if row and len(row) == 4:
                            try:
                                date_obj = datetime.strptime(row[0], "%Y-%m-%d")
                                month_key = date_obj.strftime("%B-%Y")
                                totals[month_key] = totals.get(month_key, 0) + float(row[2])
                            except ValueError:
                                continue
            report_text = "--- Monthly Spending ---\n\n"
            if not totals:
                report_text += "No data available."
            else:
                for month, total in totals.items():
                    report_text += f"{month}: ₹{total:.2f}\n"
            messagebox.showinfo("Monthly Report", report_text)
        except Exception as e:
            messagebox.showerror("Report Error", f"Could not generate report: {e}")

    def generate_category_report(self):
        totals = {}
        try:
            if os.path.exists(FILENAME):
                with open(FILENAME, mode='r', encoding='utf-8') as file:
                    reader = csv.reader(file)
                    next(reader)
                    for row in reader:
                        if row and len(row) == 4:
                            try:
                                cat = row[1]
                                totals[cat] = totals.get(cat, 0) + float(row[2])
                            except ValueError:
                                continue
            report_text = "--- Spending by Category ---\n\n"
            if not totals:
                report_text += "No data available."
            else:
                for cat, total in sorted(totals.items()):
                    report_text += f"{cat}: ₹{total:.2f}\n"
            messagebox.showinfo("Category Report", report_text)
        except Exception as e:
            messagebox.showerror("Report Error", f"Could not generate report: {e}")

    def visualize_categories(self):
        """Create pie chart and bar chart visualization for expense categories"""
        totals = {}
        try:
            if os.path.exists(FILENAME):
                with open(FILENAME, mode='r', encoding='utf-8') as file:
                    reader = csv.reader(file)
                    next(reader)
                    for row in reader:
                        if row and len(row) == 4:
                            try:
                                cat = row[1]
                                totals[cat] = totals.get(cat, 0) + float(row[2])
                            except ValueError:
                                continue
            
            if not totals:
                messagebox.showinfo("Visualization", "No expense data available to visualize.")
                return
            
            # Initialize all categories with zero values
            all_categories = ["Food", "Travel", "Bills", "Shopping", "Health", "Other"]
            for cat in all_categories:
                if cat not in totals:
                    totals[cat] = 0
            
            # Create visualization window
            vis_window = tk.Toplevel(self.root)
            vis_window.title("Expense Category Visualization")
            vis_window.geometry("800x600")
            
            # Create notebook for multiple visualization types
            notebook = ttk.Notebook(vis_window)
            notebook.pack(fill='both', expand=True, padx=10, pady=10)
            
            # Tab 1: Pie Chart
            pie_frame = ttk.Frame(notebook)
            notebook.add(pie_frame, text="Pie Chart")
            
            fig_pie = Figure(figsize=(6, 4))
            ax_pie = fig_pie.add_subplot(111)
            
            # Filter out categories with zero values for pie chart
            pie_categories = [cat for cat in all_categories if totals[cat] > 0]
            pie_values = [totals[cat] for cat in pie_categories]
            
            if pie_values:
                colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#ff99cc', '#c2c2f0']
                wedges, texts, autotexts = ax_pie.pie(pie_values, labels=pie_categories, autopct='%1.1f%%', 
                                                     startangle=90, colors=colors[:len(pie_categories)])
                ax_pie.set_title("Expenses by Category (Pie Chart)")
                
                # Style the percentage texts
                for autotext in autotexts:
                    autotext.set_color('white')
                    autotext.set_fontweight('bold')
            else:
                ax_pie.text(0.5, 0.5, 'No data to display', horizontalalignment='center', 
                           verticalalignment='center', transform=ax_pie.transAxes)
                ax_pie.set_title("No Data Available")
            
            canvas_pie = FigureCanvasTkAgg(fig_pie, master=pie_frame)
            canvas_pie.draw()
            canvas_pie.get_tk_widget().pack(fill='both', expand=True)
            
            # Tab 2: Bar Chart
            bar_frame = ttk.Frame(notebook)
            notebook.add(bar_frame, text="Bar Chart")
            
            fig_bar = Figure(figsize=(6, 4))
            ax_bar = fig_bar.add_subplot(111)
            
            categories = list(totals.keys())
            values = list(totals.values())
            
            bars = ax_bar.bar(categories, values, color=['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#ff99cc', '#c2c2f0'])
            ax_bar.set_title("Expenses by Category (Bar Chart)")
            ax_bar.set_ylabel("Amount (₹)")
            ax_bar.tick_params(axis='x', rotation=45)
            
            # Add value labels on bars
            for bar, value in zip(bars, values):
                height = bar.get_height()
                if height > 0:  # Only show label if value is positive
                    ax_bar.text(bar.get_x() + bar.get_width()/2., height,
                               f'₹{value:.2f}', ha='center', va='bottom')
            
            fig_bar.tight_layout()
            canvas_bar = FigureCanvasTkAgg(fig_bar, master=bar_frame)
            canvas_bar.draw()
            canvas_bar.get_tk_widget().pack(fill='both', expand=True)
            
            # Tab 3: Detailed Breakdown
            detail_frame = ttk.Frame(notebook)
            notebook.add(detail_frame, text="Detailed Breakdown")
            
            # Create treeview for detailed view
            detail_tree = ttk.Treeview(detail_frame, columns=("Category", "Amount", "Percentage"), show='headings', height=15)
            detail_tree.heading("Category", text="Category")
            detail_tree.heading("Amount", text="Amount (₹)")
            detail_tree.heading("Percentage", text="Percentage")
            
            detail_tree.column("Category", width=150)
            detail_tree.column("Amount", width=150)
            detail_tree.column("Percentage", width=100)
            
            scrollbar_detail = ttk.Scrollbar(detail_frame, orient="vertical", command=detail_tree.yview)
            detail_tree.configure(yscrollcommand=scrollbar_detail.set)
            scrollbar_detail.pack(side="right", fill="y")
            detail_tree.pack(side="left", fill="both", expand=True)
            
            # Calculate total and percentages
            total_amount = sum(totals.values())
            for category in all_categories:
                amount = totals[category]
                percentage = (amount / total_amount * 100) if total_amount > 0 else 0
                detail_tree.insert("", "end", values=(category, f"₹{amount:.2f}", f"{percentage:.1f}%"))
            
        except Exception as e:
            messagebox.showerror("Visualization Error", f"Could not generate chart: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    style = ttk.Style(root)
    style.theme_use('clam')
    app = BudgetTrackerApp(root)
    root.mainloop()
