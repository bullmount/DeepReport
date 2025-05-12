using DeepReport.Components.Layout;

namespace DeepReport.Services;

public interface IEventAggregator
{
  void Subscribe(IAppDispatcher dispatcherProvider);
  void Unsubscribe(IAppDispatcher dispatcherProvider);
  public void Dispatch(EventData evento);
}