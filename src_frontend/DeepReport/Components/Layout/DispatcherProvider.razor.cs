using Microsoft.AspNetCore.Components;
using DeepReport.Services;
using Fluxor;
using Fluxor.Blazor.Web.Components;

namespace DeepReport.Components.Layout
{
  public interface IAppDispatcher
  {
    void Dispatch(object action);
  }

  public partial class DispatcherProvider : FluxorComponent, 
    IAppDispatcher, IAsyncDisposable
  {
    [Inject] private IDispatcher Dispatcher { get; set; } = default!;
    [Inject] private IEventAggregator _eventAggregator { get; set; }

    protected override Task OnInitializedAsync()
    {
      _eventAggregator.Subscribe(this);
      return base.OnInitializedAsync();
    }

    public async ValueTask DisposeAsync()
    {
      _eventAggregator.Unsubscribe(this);
      await base.DisposeAsync();
    }

    public void Dispatch(object action)
    {
      InvokeAsync(() =>
      {
        Dispatcher.Dispatch(action);
      });

    }
  }
}