namespace DeepReport.Store;

public abstract class DeepResearchReducersActions
{
  public record StartDeepResearchAction(string Topic);

  public record SetStateAction(EReportState state, EventData? eventData=null);

  public record SetErrorAction(string Message);

  public record SetWaitingAction(bool isWaiting);

  public record SetSezioniAction(List<ReportSection> ElencoSezioni);

  public record SetSezioneStateAction(string Message, SectionData DatiSezione);
}