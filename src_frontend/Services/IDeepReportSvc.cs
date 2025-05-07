using System.ComponentModel;
using static DeepReport.Services.DeepReportSvc;

namespace DeepReport.Services;

public interface IDeepReportSvc
{
  Task<ResearchResult> StartDeepResearch(string topic, DeepResearchConfig deepResearchConfig);
  Task<ApprovePlanResult> ApprovePlan();
  Task<AbortResult> AbortReport();
  Task<PlanFeedbackResult> PlanFeedback(string feedback);
}


public class DeepResearchConfig
{
  public int number_of_queries { get; set; } = 2;
  public int max_search_depth { get; set; } = 2;
  public int max_results_per_query { get; set; } = 4;
  public string search_api { get; set; } = ESearchApi.googlesearch.ToString();
  public bool fetch_full_page { get; set; } = true;
  public List<string> sites_search_restriction { get; set; } = [];
}


public enum ESearchApi
{
  [Description("Google")] googlesearch,
  [Description("Duck Duck GO")] duckduckgo,
  [Description("Tavily")] tavily
}