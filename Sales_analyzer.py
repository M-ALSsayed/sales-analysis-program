import pandas as pd
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

console = Console()

try:
    load = pd.read_csv('Sales_data_analyzer/Sales_data.csv', parse_dates=['date'])
    required_columns = {"product", "quantity", "price", "order_id", "date", "category"}
except FileNotFoundError:
    console.print("[bold red]Error: Sales_data.csv file not found. Make sure the file exists.[/bold red]")
    exit()
except ValueError as e:
    console.print(f"[bold red]Error: {e}[/bold red]")
    exit()

def calc_total_revenue(data):
    table = Table(title="Total Sales", show_lines=True)
    table.add_column("Product", justify="right", style="cyan")
    table.add_column("Quantity", style="bold magenta")
    table.add_column("Price", style="green")
    table.add_column("Total", style="yellow")
    
    total_revenue = (load["price"] * load["quantity"]).sum()
    table.add_row("All Products", str(load["quantity"].sum()), str(load["price"].sum()), f"${total_revenue:.2f}")
    console = Console()
    console.print(table)


def avg_order_value(data):
    table = Table(title="Average Order Value", show_lines=True)
    table.add_column("Order ID", justify="right", style="cyan")
    table.add_column("Average Order Value", style="bold magenta")
  
    # Group by 'order_id' and sum the total for each order
    order_totals = data.groupby("order_id")[["price", "quantity"]].apply(lambda x: (x["price"] * x["quantity"]).sum())

    # Calculate the average order value
    avg_order_value = order_totals.mean()

    table.add_row("All Orders", f"${avg_order_value:.2f}")

    console = Console()
    console.print(table)


def top_selling_products(data):
    table = Table(title="Top Selling Products", show_lines=True)
    table.add_column("Product", justify="right", style="cyan")
    table.add_column("Quantity", style="White")
    
    top_selling_products = data.groupby("product")["quantity"].sum().sort_values(ascending=False)
    
    for product, quantity in top_selling_products.items():
        table.add_row(product, str(quantity))
    
    console = Console()
    console.print(table)
    
def validate_date(date_str):
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            console.print("[bold red]Invalid date format! Please enter in YYYY-MM-DD format.[/bold red]")
        return None
    
def filteration(data):
    

    filter_type = input("Enter 'Date' to filter by date or 'Category' to filter by category: ").strip()
    if filter_type.lower() == "date":
        while True:
            start_date = input(" Enter start date by 'yyy-mm-dd: ").strip()
            start_date = validate_date(start_date)
            if start_date:
                break
            
        while True:
            end_date = input(" Enter end date by 'yyy-mm-dd: ").strip()
            end_date = validate_date(end_date)
            if end_date:
                break
            
        filtered_by_date = data[(data['date'] >= pd.to_datetime(start_date)) & (data['date'] <= pd.to_datetime(end_date))]  # Filter by date range
        console.print("\nFiltered by Date:")
        console.print(filtered_by_date)    
        
    elif filter_type.lower() == "category":
        available_categories = {category.lower(): category for category in data["category"].unique()}  # Store lowercase keys with original values
        console.print(f"Available Categories: [bold yellow]{', '.join(available_categories)}[/bold yellow]")
        while True:
            category_filter = input("Enter category to filter: ").strip().lower()
            if category_filter in available_categories:
                category_filter = available_categories[category_filter]
                break
            console.print("[bold red]Invalid category! Please choose from the available categories.[/bold red]")
            
        filtered_by_category = data[data['category'] == category_filter]
        console.print(f"\nFiltered by Category ({category_filter}):")
        console.print(filtered_by_category)
    
def sales_trends(data):
    data["date"] = pd.to_datetime(data["date"])
    data["month"] = data["date"].dt.to_period("M")
    
    monthly_sales = data.groupby("month").apply(lambda x: (x["price"] * x["quantity"]).sum())
    
    table = Table(title="Monthly Sales Trend", show_lines=True)
    table.add_column("Month", justify="right", style="cyan")
    table.add_column("Revenue", style="green")
    table.add_column("Change (%)", style="yellow") 
    
    prev_month_revenu = None
    for month, revenue in monthly_sales.items():
        change = "N/A"
        if prev_month_revenu is not None:
            change = f"{((revenue - prev_month_revenu) / prev_month_revenu) * 100:.2f}%"
        table.add_row(str(month), f"${revenue:.2f}", change)
        prev_month_revenu = revenue
        
    console.print(table)
    
    
def best_worst_month(data):
    data["date"] = pd.to_datetime(data["date"])
    data["month"] = data["date"].dt.to_period("M")

    monthly_sales = data.groupby("month").apply(lambda x: (x["price"] * x["quantity"]).sum())

    best_month = monthly_sales.idxmax()
    worst_month = monthly_sales.idxmin()

    console.print(f"[bold green]Best Sales Month:[/bold green] {best_month} - ${monthly_sales.max():.2f}")
    console.print(f"[bold red]Worst Sales Month:[/bold red] {worst_month} - ${monthly_sales.min():.2f}")


def precent_selling_products(data):
    table = Table(title="Top Selling Products", show_lines=True)
    table.add_column("Product", justify="right", style="cyan")
    table.add_column("Quantity", style="white")
    table.add_column("Revenue %", style="yellow")

    total_revenue = (data["price"] * data["quantity"]).sum()
    top_products = data.groupby("product").apply(lambda x: (x["price"] * x["quantity"]).sum()).sort_values(ascending=False)

    for product, revenue in top_products.items():
        percentage = (revenue / total_revenue) * 100
        table.add_row(product, f"{revenue:.2f}", f"{percentage:.2f}%")

    console.print(table)


def export_to_csv (data, sales_insights):
    data.to_csv(sales_insights, index=False)
    console.print(f"[bold green]Data exported successfully as {sales_insights}[/bold green]")
    
def export_to_pdf(data, sales_insights):
    c = canvas.Canvas(sales_insights, pagesize=letter)
    c.setFont("Helvetica", 12)
    
    y_position = 750  # Starting position for text
    for i, line in enumerate(data.to_string().split("\n")):
        c.drawString(50, y_position, line)
        y_position -= 15  # Move down each line

        # Create a new page if needed
        if y_position < 50:
            c.showPage()
            c.setFont("Helvetica", 12)
            y_position = 750

    c.save()
    console.print(f"[bold green]Report saved as {sales_insights}[/bold green]")




def show_menu():
    menu_text = """
    [bold cyan]Sales Analysis System[/bold cyan]
    [bold white]1.[/bold white] calculate total revenue
    [bold white]2.[/bold white] calculate average order value
    [bold white]3.[/bold white] Top selling products
    [bold white]4.[/bold white] filter sales
    [bold white]5.[/bold white] sales trends
    [bold white]6.[/bold white] best or worstmonth
    [bold white]7.[/bold white] precent selling products
    [bold white]8.[/bold white] Export to CSV format
    [bold white]9.[/bold white] Export to PDF format
    [bold white]0.[/bold white] Exit
     """
    console.print(Panel(menu_text, title="[bold yellow]Menu[/bold yellow]", border_style="blue"))


def main():
    while True:
        data = load
        show_menu()
        choice = input("Enter choice: ").strip()
        if choice == "1":
            calc_total_revenue(data)
        elif choice == "2":
            avg_order_value(data)
        elif choice == "3":
            top_selling_products(data)
        elif choice == "4":
            filteration(data)
        elif choice == "5":
            sales_trends(data)
        elif choice == "6":
            best_worst_month(data)
        elif choice == "7":
            precent_selling_products(data)
        elif choice == "8":
            sales_insights = input("Enter the filename for CSV export: ").strip()
            export_to_csv(data, sales_insights)
        elif choice == "9":
            sales_insights = input("Enter the filename for PDF export: ").strip()
            export_to_pdf(data, sales_insights)
        elif choice == "0":
            break
        else:
            console.print("[bold red]Invalid choice. Please try again.[/bold red]")
    console.print("[bold cyan]Goodbye![/bold cyan]")
            

main()