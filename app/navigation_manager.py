import tkinter as tk
from tkinter import simpledialog, messagebox

class InventoryNavigationManager:
    def __init__(self, inventory_manager):
        self.inventory_manager = inventory_manager
        
    def setup_keyboard_navigation(self, ui_components):
        """Setup keyboard navigation between input fields"""
        # Left/Right navigation between fields (only when caret at ends) and Enter to Add
        ui_components.product_name_entry.bind("<Right>", lambda e: self._move_if_at_end(ui_components.product_name_entry, ui_components.product_quantity_entry))
        ui_components.product_name_entry.bind("<Left>", lambda e: self._move_if_at_start(ui_components.product_name_entry, ui_components.product_category_entry))
        ui_components.product_name_entry.bind("<Return>", lambda e: (self.inventory_manager.add_item(), "break"))

        ui_components.product_quantity_entry.bind("<Right>", lambda e: self._move_if_at_end(ui_components.product_quantity_entry, ui_components.product_price_entry))
        ui_components.product_quantity_entry.bind("<Left>", lambda e: self._move_if_at_start(ui_components.product_quantity_entry, ui_components.product_name_entry))
        ui_components.product_quantity_entry.bind("<Return>", lambda e: (self.inventory_manager.add_item(), "break"))

        ui_components.product_price_entry.bind("<Right>", lambda e: self._move_if_at_end(ui_components.product_price_entry, ui_components.product_category_entry))
        ui_components.product_price_entry.bind("<Left>", lambda e: self._move_if_at_start(ui_components.product_price_entry, ui_components.product_quantity_entry))
        ui_components.product_price_entry.bind("<Return>", lambda e: (self.inventory_manager.add_item(), "break"))

        ui_components.product_category_entry.bind("<Right>", lambda e: self._move_if_at_end(ui_components.product_category_entry, ui_components.product_name_entry))
        ui_components.product_category_entry.bind("<Left>", lambda e: self._move_if_at_start(ui_components.product_category_entry, ui_components.product_price_entry))
        ui_components.product_category_entry.bind("<Return>", lambda e: (self.inventory_manager.add_item(), "break"))

        # Bind arrow keys for navigation
        ui_components.product_name_entry.bind("<Down>", self.move_to_quantity)
        ui_components.product_quantity_entry.bind("<Up>", self.move_to_product_name)
        ui_components.product_quantity_entry.bind("<Down>", self.move_to_price)
        ui_components.product_price_entry.bind("<Up>", self.move_to_quantity)
        ui_components.product_price_entry.bind("<Down>", self.move_to_category)
        ui_components.product_category_entry.bind("<Up>", self.move_to_price)
        
    def move_to_product_name(self, event=None):
        """Move focus to product name field"""
        self.inventory_manager.ui_components.product_name_entry.focus_set()

    def move_to_quantity(self, event=None):
        """Move focus to quantity field"""
        self.inventory_manager.ui_components.product_quantity_entry.focus_set()

    def move_to_price(self, event=None):
        """Move focus to price field"""
        self.inventory_manager.ui_components.product_price_entry.focus_set()

    def move_to_category(self, event=None):
        """Move focus to category field"""
        self.inventory_manager.ui_components.product_category_entry.focus_set()

    def _move_if_at_end(self, entry_widget, next_widget):
        """Move to next widget if cursor is at end of current widget"""
        try:
            if entry_widget.index(tk.INSERT) >= len(entry_widget.get()):
                next_widget.focus_set()
                return "break"
        except Exception:
            pass
        return None

    def _move_if_at_start(self, entry_widget, prev_widget):
        """Move to previous widget if cursor is at start of current widget"""
        try:
            if entry_widget.index(tk.INSERT) <= 0:
                prev_widget.focus_set()
                return "break"
        except Exception:
            pass
        return None
        
    def position_divider_and_controls(self, table_manager):
        """Position the divider and +/- controls for the table"""
        try:
            # Divider: compute x after Category column '#6' from header bbox
            # Use the first row bbox as fallback for x-position
            first_row = next(iter(table_manager.inventory_tree.get_children('')), None)
            header_bbox = table_manager.inventory_tree.bbox(first_row, '#6') if first_row else None
            if header_bbox:
                x, y, width, height = header_bbox
                x_pos = x + width - 1
                tree_height = table_manager.inventory_tree.winfo_height()
                table_manager._divider_line.place(x=x_pos, y=0, width=2, height=tree_height)
                table_manager._divider_glow.place(x=x_pos+2, y=0, width=1, height=tree_height)
            else:
                table_manager._divider_line.place_forget()
                table_manager._divider_glow.place_forget()
        except Exception:
            pass

        # Controls: ensure +/- controls exist for each visible row in Stock column '#3'
        visible_rows = table_manager.inventory_tree.get_children('')
        for row_id in visible_rows:
            bbox = table_manager.inventory_tree.bbox(row_id, '#3')
            if not bbox:
                self._destroy_stock_controls(table_manager, row_id)
                continue
            x, y, width, height = bbox
            minus_ctrl, plus_ctrl = table_manager._stock_controls.get(row_id, (None, None))
            # Background based on selection/zebra
            bg = '#ffffff'
            try:
                if row_id in table_manager.inventory_tree.selection():
                    bg = '#dbeafe'
                else:
                    tags = table_manager.inventory_tree.item(row_id, 'tags')
                    bg = '#f9f9f9' if ('oddrow' in tags) else '#ffffff'
            except Exception:
                pass
            if minus_ctrl is None:
                minus_ctrl = tk.Label(table_manager.inventory_tree, text='−', fg='#ef4444', bg=bg, cursor='hand2', font=('Segoe UI', 13, 'bold'))
                minus_ctrl.bind('<Button-1>', lambda e, r=row_id: self._prompt_adjust_stock(r, -1))
            if plus_ctrl is None:
                plus_ctrl = tk.Label(table_manager.inventory_tree, text='+', fg='#2563eb', bg=bg, cursor='hand2', font=('Segoe UI', 13, 'bold'))
                plus_ctrl.bind('<Button-1>', lambda e, r=row_id: self._prompt_adjust_stock(r, +1))
            try:
                minus_ctrl.configure(bg=bg)
                plus_ctrl.configure(bg=bg)
            except Exception:
                pass
            btn_h = max(20, min(28, height-4))
            btn_w = 22
            minus_ctrl.place(x=x+3, y=y+2, width=btn_w, height=btn_h)
            plus_ctrl.place(x=x+width-btn_w-3, y=y+2, width=btn_w, height=btn_h)
            table_manager._stock_controls[row_id] = (minus_ctrl, plus_ctrl)

        # Controls: ensure +/- controls exist for each visible row in Sales column '#7'
        visible_rows = table_manager.inventory_tree.get_children('')
        for row_id in visible_rows:
            bbox = table_manager.inventory_tree.bbox(row_id, '#7')
            if not bbox:
                # Row may be scrolled off; remove controls if any
                self._destroy_row_controls(table_manager, row_id)
                continue
            x, y, width, height = bbox
            minus_ctrl, plus_ctrl = table_manager._sold_controls.get(row_id, (None, None))
            # Determine background based on row state (selected/zebra)
            bg = '#ffffff'
            try:
                if row_id in table_manager.inventory_tree.selection():
                    bg = '#dbeafe'
                else:
                    tags = table_manager.inventory_tree.item(row_id, 'tags')
                    bg = '#f9f9f9' if ('oddrow' in tags) else '#ffffff'
            except Exception:
                pass
            if minus_ctrl is None:
                minus_ctrl = tk.Label(table_manager.inventory_tree, text='−', fg='#ef4444', bg=bg, cursor='hand2', font=('Segoe UI', 13, 'bold'))
                minus_ctrl.bind('<Button-1>', lambda e, r=row_id: self._prompt_adjust_sold(r, -1))
            if plus_ctrl is None:
                plus_ctrl = tk.Label(table_manager.inventory_tree, text='+', fg='#2563eb', bg=bg, cursor='hand2', font=('Segoe UI', 13, 'bold'))
                plus_ctrl.bind('<Button-1>', lambda e, r=row_id: self._prompt_adjust_sold(r, +1))
            # Update bg in case row selection/zebra changed
            try:
                minus_ctrl.configure(bg=bg)
                plus_ctrl.configure(bg=bg)
            except Exception:
                pass
            btn_h = max(20, min(28, height-4))
            btn_w = 22
            minus_ctrl.place(x=x+3, y=y+2, width=btn_w, height=btn_h)
            plus_ctrl.place(x=x+width-btn_w-3, y=y+2, width=btn_w, height=btn_h)
            table_manager._sold_controls[row_id] = (minus_ctrl, plus_ctrl)

        # Remove controls for rows no longer visible
        for row_id in list(table_manager._sold_controls.keys()):
            if row_id not in visible_rows:
                self._destroy_row_controls(table_manager, row_id)
        for row_id in list(table_manager._stock_controls.keys()):
            if row_id not in visible_rows:
                self._destroy_stock_controls(table_manager, row_id)

    def _destroy_row_controls(self, table_manager, row_id):
        """Destroy sales controls for a specific row"""
        minus_btn, plus_btn = table_manager._sold_controls.pop(row_id, (None, None))
        try:
            if minus_btn is not None:
                minus_btn.place_forget()
                minus_btn.destroy()
        except Exception:
            pass
        try:
            if plus_btn is not None:
                plus_btn.place_forget()
                plus_btn.destroy()
        except Exception:
            pass

    def _destroy_stock_controls(self, table_manager, row_id):
        """Destroy stock controls for a specific row"""
        minus_btn, plus_btn = table_manager._stock_controls.pop(row_id, (None, None))
        try:
            if minus_btn is not None:
                minus_btn.place_forget()
                minus_btn.destroy()
        except Exception:
            pass
        try:
            if plus_btn is not None:
                plus_btn.place_forget()
                plus_btn.destroy()
        except Exception:
            pass

    def _prompt_adjust_sold(self, row_id, sign):
        """Prompt user to adjust sold quantity"""
        try:
            values = list(self.inventory_manager.table_manager.inventory_tree.item(row_id, 'values'))
        except Exception:
            return
        if not values:
            return
        prompt = "Increase Sales by" if sign > 0 else "Decrease Sales by"
        amount = simpledialog.askinteger("Adjust Sales", f"{prompt} (units):", parent=self.inventory_manager.root, minvalue=0)
        if amount is None:
            return
        if amount < 0:
            messagebox.showwarning("Invalid Input", "Amount cannot be negative.")
            return
        # Validate bounds strictly: cannot sell more than remaining; cannot reduce sales below zero
        try:
            remaining_qty = int(values[2])
            existing_sold = int(values[6]) if values[6] not in (None, '') else 0
        except Exception:
            return
        if sign > 0 and amount > remaining_qty:
            messagebox.showwarning("Invalid Amount", "Cannot increase sales by more than current stock.")
            return
        if sign < 0 and amount > existing_sold:
            messagebox.showwarning("Invalid Amount", "Cannot decrease sales by more than current sales.")
            return
        delta = amount if sign > 0 else -amount
        self.inventory_manager.data_operations.adjust_sold(row_id, delta)

    def _prompt_adjust_stock(self, row_id, sign):
        """Prompt user to adjust stock quantity"""
        try:
            values = list(self.inventory_manager.table_manager.inventory_tree.item(row_id, 'values'))
        except Exception:
            return
        if not values:
            return
        prompt = "Increase Stock by" if sign > 0 else "Decrease Stock by"
        amount = simpledialog.askinteger("Adjust Stock", f"{prompt} (units):", parent=self.inventory_manager.root, minvalue=0)
        if amount is None:
            return
        if amount < 0:
            messagebox.showwarning("Invalid Input", "Amount cannot be negative.")
            return
        # Validate bounds strictly for stock decreases
        try:
            remaining_qty = int(values[2])
        except Exception:
            return
        if sign < 0 and amount > remaining_qty:
            messagebox.showwarning("Invalid Amount", "Cannot decrease stock by more than current stock.")
            return
        delta = amount if sign > 0 else -amount
        self.inventory_manager.data_operations.adjust_stock(row_id, delta)
