from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from employees.models import IncentiveSlab, LoadGrowthSlab
from ..forms import IncentiveSlabForm, LoadGrowthSlabForm

@login_required
def slab_list(request):
    slabs = IncentiveSlab.objects.all()
    growth_slabs = LoadGrowthSlab.objects.all()
    return render(request, 'dashboard/slabs/slab_list.html', {
        'slabs': slabs,
        'growth_slabs': growth_slabs
    })

@login_required
def slab_create(request):
    if request.method == 'POST':
        form = IncentiveSlabForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Incentive slab created successfully.")
            return redirect('slab_list')
    else:
        form = IncentiveSlabForm()
    return render(request, 'dashboard/slabs/slab_form.html', {'form': form, 'title': 'Create Incentive Slab'})

@login_required
def slab_edit(request, pk):
    slab = get_object_or_404(IncentiveSlab, pk=pk)
    if request.method == 'POST':
        form = IncentiveSlabForm(request.POST, instance=slab)
        if form.is_valid():
            form.save()
            messages.success(request, "Incentive slab updated successfully.")
            return redirect('slab_list')
    else:
        form = IncentiveSlabForm(instance=slab)
    return render(request, 'dashboard/slabs/slab_form.html', {'form': form, 'title': 'Edit Incentive Slab'})

@login_required
def slab_delete(request, pk):
    slab = get_object_or_404(IncentiveSlab, pk=pk)
    if request.method == 'POST':
        slab.delete()
        messages.success(request, "Incentive slab deleted successfully.")
        return redirect('slab_list')
    return render(request, 'dashboard/slabs/slab_confirm_delete.html', {'slab': slab})


# Load Growth Slab Views

@login_required
def load_growth_slab_create(request):
    if request.method == 'POST':
        form = LoadGrowthSlabForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Load growth slab created successfully.")
            return redirect('slab_list')
    else:
        form = LoadGrowthSlabForm()
    return render(request, 'dashboard/slabs/slab_form.html', {'form': form, 'title': 'Create Load Growth Slab'})

@login_required
def load_growth_slab_edit(request, pk):
    slab = get_object_or_404(LoadGrowthSlab, pk=pk)
    if request.method == 'POST':
        form = LoadGrowthSlabForm(request.POST, instance=slab)
        if form.is_valid():
            form.save()
            messages.success(request, "Load growth slab updated successfully.")
            return redirect('slab_list')
    else:
        form = LoadGrowthSlabForm(instance=slab)
    return render(request, 'dashboard/slabs/slab_form.html', {'form': form, 'title': 'Edit Load Growth Slab'})

@login_required
def load_growth_slab_delete(request, pk):
    slab = get_object_or_404(LoadGrowthSlab, pk=pk)
    if request.method == 'POST':
        slab.delete()
        messages.success(request, "Load growth slab deleted successfully.")
        return redirect('slab_list')
    return render(request, 'dashboard/slabs/slab_confirm_delete.html', {'slab': slab, 'is_growth': True})
