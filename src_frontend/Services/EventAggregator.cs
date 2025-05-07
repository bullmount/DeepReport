using DeepReport.Components.Layout;
using DeepReport.Store;

namespace DeepReport.Services
{
  public class EventAggregator : IEventAggregator
  {
    private List<IAppDispatcher> _appDispathcers = [];

    public void Subscribe(IAppDispatcher dispatcherProvider)
    {
      if (_appDispathcers.Any(x => x == dispatcherProvider))
        return;
      _appDispathcers.Add(dispatcherProvider);
    }

    public void Unsubscribe(IAppDispatcher dispatcherProvider)
    {
      _appDispathcers.RemoveAll(x => x == dispatcherProvider);
    }

    public void Dispatch(EventData evento)
    {
      foreach (var appDispatcher in _appDispathcers)
      {
        appDispatcher?.Dispatch(new DeepResearchReducersActions.SetStateAction(evento.state.Value, evento));

      }
    }
  }
}