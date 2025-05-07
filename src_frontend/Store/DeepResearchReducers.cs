using Fluxor;

namespace DeepReport.Store;

public class DeepResearchReducers
{
  [ReducerMethod]
  public DeepResearchState Handle(DeepResearchState state, DeepResearchReducersActions.SetSezioneStateAction action)
  {
    var sezione = state.Sezioni.FirstOrDefault(x => x.Posizione == action.DatiSezione.Sezione_Posizione);
    if (sezione == null)
      return state;
    sezione.Fase = action.DatiSezione.Fase;
    sezione.SearchIterations = action.DatiSezione.Search_Iterations;
    sezione.LastMessage = action.Message;
    return state;
  }

  [ReducerMethod]
  public DeepResearchState Handle(DeepResearchState state, DeepResearchReducersActions.SetSezioniAction action)
  {
    return state with { Sezioni= action.ElencoSezioni };
  }

  [ReducerMethod]
  public DeepResearchState Handle(DeepResearchState state, DeepResearchReducersActions.StartDeepResearchAction action)
  {
    return state with { Topic = action.Topic,Stato = EReportState.Started};
  }

  [ReducerMethod]
  public DeepResearchState Handle(DeepResearchState state, DeepResearchReducersActions.SetErrorAction action)
  {
    return state with { Stato = EReportState.NotStarted, Error = true, LastErrorMessage = action.Message};
  }

  [ReducerMethod]
  public DeepResearchState Handle(DeepResearchState state, DeepResearchReducersActions.SetStateAction action)
  {
    return state with { Stato = action.state };
  }

  [ReducerMethod]
  public DeepResearchState Handle(DeepResearchState state, DeepResearchReducersActions.SetWaitingAction action)
  {
    return state with { IsWaiting = action.isWaiting};
  }
}