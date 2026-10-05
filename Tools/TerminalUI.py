from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.rule import Rule


console = Console()


def show_header():
    console.print()

    console.print(Panel("[bold]CentrAlign[/bold]\n""[dim]AI Worker[/dim]",border_style="bright_blue",padding=(0, 2)))

    
def show_loading(message: str):
    return console.status(
        f"[bold cyan]{message}[/bold cyan]",
        spinner="dots"
    )

def show_user_request(request: str):
    console.print()

    text = Text()
    text.append("❯ ", style="bold cyan")
    text.append(request)

    console.print(text)


def show_planning(plan):
    console.print()
    console.print("[bold cyan]● Planning[/bold cyan]")

    console.print(
        f"  [green]✓[/green] {len(plan)} task(s) planned"
    )


def show_plan_details(plan):
    if not plan:
        return

    table = Table(
        show_header=True,
        header_style="bold",
        box=None,
        padding=(0, 2)
    )

    table.add_column("Task", style="dim", width=6)
    table.add_column("Action", style="cyan")
    table.add_column("Description")

    for task in plan:
        table.add_row(
            str(task["id"]),
            task["action"],
            task.get("description", "")
        )

    console.print(table)


def show_execution(history):
    console.print()
    console.print("[bold cyan]● Executing[/bold cyan]")

    for item in history:

        action = item["action"]
        result = item["result"]

        if result.get("success", False):

            console.print(
                f"  [green]✓[/green] "
                f"[cyan]{action}[/cyan]"
            )

            path = result.get("path")

            if path:
                console.print(
                    f"    [dim]{path}[/dim]"
                )

        else:

            console.print(
                f"  [red]✗[/red] "
                f"[cyan]{action}[/cyan]"
            )

            error = result.get(
                "error",
                "Unknown error"
            )

            console.print(
                f"    [red]{error}[/red]"
            )


def show_result(result):
    console.print()

    if result["status"] in ["executed", "completed"]:

        console.print(
            Panel(
                "[bold green]✓ Task completed successfully[/bold green]",
                border_style="green",
                padding=(0, 2)
            )
        )

    else:

        error = result.get(
            "error",
            "The task could not be completed."
        )

        console.print(
            Panel(
                f"[bold red]✗ Task failed[/bold red]\n\n"
                f"[red]{error}[/red]",
                border_style="red",
                padding=(0, 2)
            )
        )


def show_final_response(response: str):

    console.print()

    console.print(
        Rule(
            "CentrAlign",
            style="dim"
        )
    )

    console.print()

    console.print(
        Panel(
            response,
            border_style="dim",
            padding=(1, 2)
        )
    )

    console.print()