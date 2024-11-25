import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import openpyxl
from openpyxl import Workbook
import os
import cv2

# Create main window
root = tk.Tk()
root.title("Billing System")
root.geometry("1000x700")
cart = []
image_path = None
image_display = None  # Variable to store the image object reference

# Scrollable frame setup
scrollable_frame = tk.Frame(root)
scrollable_frame.pack(fill=tk.BOTH, expand=True)
canvas = tk.Canvas(scrollable_frame)
canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar = tk.Scrollbar(scrollable_frame, orient="vertical", command=canvas.yview)
scrollbar.pack(side=tk.RIGHT, fill="y")
canvas.configure(yscrollcommand=scrollbar.set)
canvas.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

# Main content frame
content_frame = tk.Frame(canvas)
canvas.create_window((0, 0), window=content_frame, anchor="nw")

# Header
header_label = tk.Label(content_frame, text="Billing System", font=("Arial", 24, "bold"))
header_label.pack(side=tk.TOP, pady=10)

# Customer Details Frame
customer_frame = tk.LabelFrame(content_frame, text="Customer Details", font=("Arial", 14, "bold"))
customer_frame.pack(fill=tk.X, padx=10, pady=10)

tk.Label(customer_frame, text="Bill Number", font=("Arial", 12)).grid(row=0, column=0, padx=5, pady=5)
bill_number_entry = tk.Entry(customer_frame, font=("Arial", 12))
bill_number_entry.grid(row=0, column=1, padx=5, pady=5)



tk.Label(customer_frame, text="Customer Name", font=("Arial", 12)).grid(row=0, column=2, padx=5, pady=5)
customer_name_entry = tk.Entry(customer_frame, font=("Arial", 12))
customer_name_entry.grid(row=0, column=3, padx=5, pady=5)

tk.Label(customer_frame, text="Contact Number", font=("Arial", 12)).grid(row=0, column=4, padx=5, pady=5)
contact_number_entry = tk.Entry(customer_frame, font=("Arial", 12))
contact_number_entry.grid(row=0, column=5, padx=5, pady=5)

# Main Content Frame
main_content_frame = tk.Frame(content_frame)
main_content_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

# Bill Window Frame
bill_window_frame = tk.LabelFrame(main_content_frame, text="Bill Window", font=("Arial", 14, "bold"))
bill_window_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

bill_text = tk.Text(bill_window_frame, font=("Arial", 12), height=20)
bill_text.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

# Product Details Frame
product_frame = tk.LabelFrame(main_content_frame, text="Product Details", font=("Arial", 14, "bold"))
product_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

tk.Label(product_frame, text="Product Name", font=("Arial", 12)).grid(row=0, column=0, padx=5, pady=5)
product_name_entry = tk.Entry(product_frame, font=("Arial", 12))
product_name_entry.grid(row=0, column=1, padx=20, pady=5)

tk.Label(product_frame, text="Quantity", font=("Arial", 12)).grid(row=1, column=0, padx=5, pady=5)
quantity_entry = tk.Entry(product_frame, font=("Arial", 12))
quantity_entry.grid(row=1, column=1, padx=20, pady=5)

tk.Label(product_frame, text="Price", font=("Arial", 12)).grid(row=2, column=0, padx=5, pady=5)
price_entry = tk.Entry(product_frame, font=("Arial", 12))
price_entry.grid(row=2, column=1, padx=20, pady=5)

tk.Label(product_frame, text="Total", font=("Arial", 12)).grid(row=3, column=0, padx=5, pady=5)
total_label = tk.Label(product_frame, text="0.00", font=("Arial", 12))
total_label.grid(row=3, column=1, padx=20, pady=5)

# Image display label
image_label = tk.Label(product_frame)  # Label to display the imported image
image_label.grid(row=4, column=0, columnspan=2, pady=10)

def import_photo():
    global image_path
    global image_display
    image_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
    if image_path:
        # Load image using OpenCV
        img = cv2.imread(image_path)
        img = cv2.resize(img, (200, 200))  # Resize image to fit label
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # Convert BGR to RGB
        img_pil = Image.fromarray(img_rgb)  # Convert to PIL Image
        image_display = ImageTk.PhotoImage(img_pil)  # Convert to PhotoImage for Tkinter
        image_label.config(image=image_display)  # Display the image in the label

import_button = tk.Button(product_frame, text="Import Photo", font=("Arial", 12), command=import_photo)
import_button.grid(row=5, column=0, columnspan=2, pady=5)  # Moved below image label

def update_total_price(*args):
    try:
        quantity = int(quantity_entry.get())
        price = float(price_entry.get())
        total = quantity * price
        total_label.config(text=f"{total:.2f}")
    except ValueError:
        total_label.config(text="0.00")

quantity_entry.bind("<KeyRelease>", update_total_price)
price_entry.bind("<KeyRelease>", update_total_price)

def select_payment_method():
    payment_window = tk.Toplevel(root)
    payment_window.title("Select Payment Method")
    payment_var = tk.StringVar(value="Cash")  # Default selection

    tk.Label(payment_window, text="Select Payment Method:", font=("Arial", 14)).pack(pady=10)
    tk.Radiobutton(payment_window, text="Cash", variable=payment_var, value="Cash", font=("Arial", 12)).pack(anchor=tk.W)
    tk.Radiobutton(payment_window, text="Online Payment", variable=payment_var, value="Online Payment", font=("Arial", 12)).pack(anchor=tk.W)

    def confirm_selection():
        payment_method = payment_var.get()
        payment_window.destroy()  # Close the payment selection window
        add_to_cart(payment_method)  # Pass the selected payment method

    tk.Button(payment_window, text="Confirm", command=confirm_selection, font=("Arial", 12)).pack(pady=10)

def add_to_cart(payment_method):
    global image_path
    product_name = product_name_entry.get()
    quantity = quantity_entry.get()
    price = price_entry.get()

    if not (product_name and quantity and price):
        messagebox.showerror("Input Error", "Please fill in all fields")
        return
    try:
        quantity = int(quantity)
        price = float(price)
    except ValueError:
        messagebox.showerror("Input Error", "Quantity and Price must be numbers")
        return
    
    total = quantity * price
    cart.append((product_name, quantity, price, total, payment_method))  # Include payment method
    bill_text.delete(1.0, tk.END)

    for item in cart:
        bill_text.insert(tk.END, f"Product: {item[0]}, Quantity: {item[1]}, Price: {item[2]:.2f}, Total: {item[3]:.2f}, Payment: {item[4]}\n")
    bill_text.insert(tk.END, f"\nTotal Bill: {sum(item[3] for item in cart):.2f}\n")
    
    if save_customer_details_to_excel():
        messagebox.showinfo("Success", "Customer details saved to Excel successfully.")

def save_customer_details_to_excel():
    file_path = "customer_details.xlsx"
    if not os.path.exists(file_path):
        workbook = Workbook()
        sheet = workbook.active
        sheet.append(["Bill Number", "Customer Name", "Contact Number", "Product Name", "Quantity", "Price", "Total", "Payment Method"])
    else:
        workbook = openpyxl.load_workbook(file_path)
        sheet = workbook.active

    for item in cart:
        sheet.append([bill_number_entry.get(), customer_name_entry.get(), contact_number_entry.get(),
                       item[0], item[1], item[2], item[3], item[4]])  # Include payment method

    workbook.save(file_path)
    return True  # Indicate success

def clear_fields():
    product_name_entry.delete(0, tk.END)
    quantity_entry.delete(0, tk.END)
    price_entry.delete(0, tk.END)

clear_fields_button = tk.Button(product_frame, text="Clear Fields", font=("Arial", 12), command=clear_fields)
clear_fields_button.grid(row=6, column=0, columnspan=2, pady=5)

# Bill Options Frame
bill_options_frame = tk.LabelFrame(content_frame, text="Bill Options", font=("Arial", 14, "bold"), bg="lightgray")
bill_options_frame.pack(fill=tk.X, padx=10, pady=10)

generate_button = tk.Button(bill_options_frame, text="Generate Bill", font=("Arial", 12), bg="green", fg="white", command=select_payment_method)
generate_button.pack(side=tk.LEFT, padx=10, pady=10)

clear_bill_button = tk.Button(bill_options_frame, text="Clear Bill", font=("Arial", 12), bg="orange", fg="white", command=lambda: bill_text.delete(1.0, tk.END))
clear_bill_button.pack(side=tk.LEFT, padx=10, pady=10)

exit_button = tk.Button(bill_options_frame, text="Exit", font=("Arial", 12), bg="red", fg="white", command=root.quit)
exit_button.pack(side=tk.LEFT, padx=10, pady=10)

def print_bill():
    # Create a new window for printing the bill
    print_window = tk.Toplevel(root)
    print_window.title("Print Bill")
    print_window.geometry("400x500")

    # Add a label for the title
    tk.Label(print_window, text="Bill Details", font=("Arial", 16, "bold")).pack(pady=10)

    # Add a text widget to display the bill details
    bill_display = tk.Text(print_window, font=("Arial", 12))
    bill_display.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Copy the content of the bill_text widget into the new text widget
    bill_display.insert(tk.END, bill_text.get(1.0, tk.END))
    bill_display.configure(state=tk.DISABLED)  # Make the text widget read-only

# Add the Print button to the Bill Options Frame
print_button = tk.Button(bill_options_frame, text="Print", font=("Arial", 12), bg="blue", fg="white", command=print_bill)
print_button.pack(side=tk.LEFT, padx=10, pady=10)

# Initialize the bill number counter
current_bill_number = 1  # Starting bill number

def update_bill_number():
    """Update the bill number entry field with the next bill number."""
    global current_bill_number
    bill_number_entry.delete(0, tk.END)  # Clear the current entry
    bill_number_entry.insert(0, f"{current_bill_number:04d}")  # Display the next bill number (zero-padded)

def generate_new_bill():
    """Handle new bill generation, incrementing the bill number."""
    global current_bill_number
    if customer_name_entry.get() and contact_number_entry.get():
        # Increment bill number only if customer details are filled
        current_bill_number += 1
        update_bill_number()
        clear_fields()  # Clear product details for new bill
        cart.clear() 
        bill_text.delete(1.0, tk.END)  # Clear the bill window
    else:
        messagebox.showerror("Input Error", "Please fill in customer details before generating a new bill.")

# Add "New Bill" button to generate a new bill with updated bill number
new_bill_button = tk.Button(
    bill_options_frame, text="New Bill", font=("Arial", 12), bg="purple", fg="white", command=generate_new_bill
)
new_bill_button.pack(side=tk.LEFT, padx=10, pady=10)

# Call update_bill_number once during initialization to display the starting bill number
update_bill_number()

def generate_new_bill():
    """Handle new bill generation, incrementing the bill number and clearing fields."""
    global current_bill_number
    if customer_name_entry.get() and contact_number_entry.get():
        # Increment bill number only if customer details are filled
        current_bill_number += 1
        update_bill_number()  # Update the bill number for the next bill
        clear_fields()  # Clear product details
        clear_customer_details()  # Clear customer details
        bill_text.delete(1.0, tk.END)  # Clear the bill window
    else:
        messagebox.showerror("Input Error", "Please fill in customer details before generating a new bill.")

def clear_customer_details():
    """Clear all customer-related fields."""
    bill_number_entry.delete(0, tk.END)
    customer_name_entry.delete(0, tk.END)
    contact_number_entry.delete(0, tk.END)


# Run the application
root.mainloop()
