from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from employees.models import MonthlyTarget
from dashboard.forms import MonthlyTargetForm


@login_required
def target_list(request):
    targets = MonthlyTarget.objects.all().order_by('-month')
    return render(request, 'dashboard/targets/target_list.html', {'targets': targets})

@login_required
def target_create(request):
    if request.method == 'POST':
        form = MonthlyTargetForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Monthly target set successfully.")
            return redirect('target_list')
    else:
        form = MonthlyTargetForm()
    return render(request, 'dashboard/targets/target_form.html', {'form': form, 'title': 'Set Monthly Target'})

@login_required
def target_edit(request, pk):
    target = get_object_or_404(MonthlyTarget, pk=pk)
    if request.method == 'POST':
        form = MonthlyTargetForm(request.POST, instance=target)
        if form.is_valid():
            form.save()
            messages.success(request, "Monthly target updated successfully.")
            return redirect('target_list')
    else:
        form = MonthlyTargetForm(instance=target)
    return render(request, 'dashboard/targets/target_form.html', {'form': form, 'title': 'Edit Monthly Target'})

@login_required
def target_delete(request, pk):
    target = get_object_or_404(MonthlyTarget, pk=pk)
    if request.method == 'POST':
        target.delete()
        messages.success(request, "Monthly target deleted successfully.")
        return redirect('target_list')
    return render(request, 'dashboard/targets/target_confirm_delete.html', {'target': target})
