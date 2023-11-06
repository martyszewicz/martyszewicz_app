from django.shortcuts import render
from django.contrib import messages
from .models import Coffee, Report
from django.db.models import Sum
from .forms import User_choice, Budget_change


class Transaction:
    def __init__(self, user_choice, budget, price):
        self.user_choice = user_choice
        self.budget = float(budget)
        self.price = price

    def budget_change(self, bc):
        self.bc = bc
        if self.bc == '':
            self.bc = 0
        self.budget += float(self.bc)
        return self.budget

    def reset(self):
        self.budget = 0
        return self.budget


transaction = Transaction("", 0, 0)


def coffee_machine(request):
    user_choice_form = User_choice(request.POST)
    budget_change_form = Budget_change(request.POST)
    if request.method == 'GET':
        # Start position
        messages.success(request, 'Stand by, \nplease select coffee')
        return render(request, "coffee_machine/coffee_machine.html")
    else:
        if user_choice_form.is_valid():
            user_choice = user_choice_form.cleaned_data['user_choice']
            if user_choice == 'report':
                # If user press 'report button'
                if  transaction.budget:
                    # Report can be displayed only when there is no transaction in progress
                    messages.success(request, f'"For view a report please \nreset coffee machine"')
                else:
                    # build report from database
                    num_of_espresso = 0
                    num_of_latte = 0
                    num_of_cappuccino = 0
                    data = Report.objects.all()
                    for coffee in range(len(data)):
                        if data[coffee].name == 'espresso':
                            num_of_espresso += 1
                        if data[coffee].name == 'latte':
                            num_of_latte += 1
                        if data[coffee].name == 'cappuccino':
                            num_of_cappuccino += 1
                    result = Report.objects.aggregate(total=Sum('price'))
                    earn = result['total']
                    messages.success(request, f"Number of espresso: {num_of_espresso} \nNumber of latte: {num_of_latte} \nNumber of cappuccino: {num_of_cappuccino} \nEarn: {round(earn, 2)}")
                return render(request, "coffee_machine/coffee_machine.html")
            if user_choice == 'reset':
                # If user press 'reset' button
                if transaction.budget > 0:
                    # If user insert coins to ekspress
                    rest = round(transaction.budget, 2)
                    messages.success(request, f"Coffee machine reset, \nyour refund {rest}")
                    transaction.reset()
                else:
                    # If there is no coins in express
                    transaction.reset()
                    messages.success(request, 'Stand by, \nplease select coffee')
                return render(request, "coffee_machine/coffee_machine.html")
            if user_choice == 'accept':
                # If user press 'accept' button
                if transaction.budget >= transaction.price:
                    # Check if user insert enough coins
                    refund = transaction.budget - transaction.price
                    # Save info about transaction to database sqlite3
                    name = transaction.user_choice
                    price = transaction.price
                    new_transaction = Report(name=name, price=price)
                    new_transaction.save()
                    if refund > 0:
                        # Check refund
                        rest = round(refund, 2)
                        messages.success(request, f"Your coffee {transaction.user_choice} \nis ready, \nrefund is {rest}, enjoy")
                        transaction.reset()
                    else:
                        messages.success(request, f"Your coffee {transaction.user_choice} \nis ready, enjoy")
                        transaction.reset()
                    return render(request, "coffee_machine/coffee_machine.html")
                else:
                    # If user press 'accept' button but there is lack of coins in express
                    lack = transaction.price - transaction.budget
                    messages.success(request, f"{transaction.user_choice}. \nNot enough money, \nplease insert {round(lack, 2)} more")
                return render(request, "coffee_machine/prepare_coffee.html")
            if user_choice == "espresso" or user_choice == "latte" or user_choice == "cappuccino":
                # change information on display about order
                user_coffee = Coffee.objects.filter(name=user_choice).first()
                transaction.user_choice = user_coffee.name
                transaction.price = user_coffee.price
                messages.success(request, f"Price: {transaction.price}zł; \nYour budget: {round(transaction.budget, 2)}zł")
                return render(request, "coffee_machine/prepare_coffee.html")

        if budget_change_form.is_valid():
            budget_change = budget_change_form.cleaned_data['budget_change']
                # change user budget after insert coins
            transaction.budget_change(budget_change)
            messages.success(request, f"Price: {transaction.price}zł; \nYour budget: {round(transaction.budget, 2)}zł")
            return render(request, "coffee_machine/prepare_coffee.html")
