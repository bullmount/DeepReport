using DeepReport.Store;

namespace DeepReport;

public class EventData
{
  public string event_type { get; set; }
  public string message { get; set; }
  public DateTime timestamp { get; set; }
  public EReportState? state { get; set; }
  public string? data { get; set; }
}