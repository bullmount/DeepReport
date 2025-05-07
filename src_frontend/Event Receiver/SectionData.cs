namespace DeepReport;

public class SectionData
{
  public int Sezione_Posizione { get; set; }
  public string Sezione_Nome { get; set; } = string.Empty;
  public int Search_Iterations { get; set; }
  public List<string> Search_Queries { get; set; } = new List<string>();
  public EFaseSezioneFase Fase { get; set; }

}

public enum EFaseSezioneFase
{
  QUERY = 0,
  SEARCH = 1,
  WRITE = 2,
  COMPLETE = 3
}