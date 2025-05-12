using Fluxor;

namespace DeepReport.Store
{
  [FeatureState]
  public record DeepResearchState
  {
    public bool IsWaiting { get; set; }
    public string Topic { get; set; } = string.Empty;
    public EReportState Stato { get; set; } = EReportState.NotStarted;
    public List<ReportSection> Sezioni { get; set; } = new List<ReportSection>();
    public string ContenutoFinale { get; set; } = string.Empty;
    //public List<Fonte> Fonti { get; set; } = [];
    public bool Error { get; set; }
    public string LastErrorMessage { get; set; }
  }

  //public class Fonte
  //{
  //  public int Numero { get; set; }
  //  public string Url { get; set; } = string.Empty;
  //  public string Snippet { get; set; } = string.Empty;
  //}

  public class ReportSection
  {
    public int Posizione { get; set; } 
    public string Titolo { get; set; } = string.Empty;
    public string Descrizione { get; set; } = string.Empty;
    public string Contenuto { get; set; } = string.Empty;
    public bool Richiede_ricerca { get; set; } = false;

    //public ESectionState Stato { get; set; } = ESectionState.NotStarted;
    //public List<Fonte> Fonti { get; set; } = [];
    public EFaseSezioneFase? Fase { get; set; }
    public int SearchIterations { get; set; }
    public string LastMessage { get; set; }
  }



  //public enum ESectionState
  //{
  //  NotStarted,
  //  Searching,
  //  Writing,
  //  Validating,
  //  Completed,
  //}


  public enum EReportState
  {
    NotStarted = 0,
    Started = 1,
    Searching = 2,
    Planning = 3,
    WaitingForApproval = 4,
    Approved = 5,
    WritingSection = 6,
    Reviewing = 7,
    Canceled = 8,
    Completed = 9,
    //----
    Aborted = 10,
    Error = 11
  }
}
