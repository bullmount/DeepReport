using DeepReport.Services;
using Fluxor;

namespace DeepReport.Store;

public class DeepResearchEffects
{
  private readonly IDeepReportSvc _deepReportSvc;

  public DeepResearchEffects(IDeepReportSvc deepReportSvc)
  {
    _deepReportSvc = deepReportSvc;
  }

  [EffectMethod]
  public async Task Handle(DeepResearchEffectsActions.AbortReportAction action, IDispatcher dispatcher)
  {
    dispatcher.Dispatch(new DeepResearchReducersActions.SetWaitingAction(true));
    try
    {
      var res = await _deepReportSvc.AbortReport();
      if (!res.Success)
        dispatcher.Dispatch(new DeepResearchReducersActions.SetErrorAction(res.Message));
    }
    catch (Exception e)
    {
      dispatcher.Dispatch(new DeepResearchReducersActions.SetWaitingAction(false));
      dispatcher.Dispatch(new DeepResearchReducersActions.SetErrorAction(e.Message));
    }
    finally
    {
      dispatcher.Dispatch(new DeepResearchReducersActions.SetWaitingAction(false));
    }
  }

  [EffectMethod]
  public async Task Handle(DeepResearchEffectsActions.SetTopicAction action, IDispatcher dispatcher)
  {
    dispatcher.Dispatch(new DeepResearchReducersActions.SetWaitingAction(true));
    try
    {
      var res = await _deepReportSvc.StartDeepResearch(action.Topic, action.DeepResearchConfig);
      if (res.Success)
        dispatcher.Dispatch(new DeepResearchReducersActions.StartDeepResearchAction(action.Topic));
      else
        dispatcher.Dispatch(new DeepResearchReducersActions.SetErrorAction(res.Message));
      await Task.CompletedTask;
    }
    finally
    {
      dispatcher.Dispatch(new DeepResearchReducersActions.SetWaitingAction(false));
    }
  }
}