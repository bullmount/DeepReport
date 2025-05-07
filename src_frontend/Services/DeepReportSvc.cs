namespace DeepReport.Services;

public class DeepReportSvc : IDeepReportSvc
{
  private readonly IHttpClientFactory _clientFactory;

  public DeepReportSvc(IHttpClientFactory clientFactory)
  {
    _clientFactory = clientFactory;
  }

  public async Task<ResearchResult> StartDeepResearch(string topic, DeepResearchConfig deepResearchConfig)
  {
    using var client = _clientFactory.CreateClient("FastApi");
    var data = new ResearchRequest { Topic = topic, Config = deepResearchConfig };
    try
    {
      var response = await client.PostAsJsonAsync("deepresearch", data);
      if (!response.IsSuccessStatusCode)
        return new ResearchResult() { Success = false, Message = $"Errore {response.StatusCode} nella chiamata API" };

      var result = await response.Content.ReadFromJsonAsync<ResearchResult>();
      return result;
    }
    catch (Exception e)
    {
      return new ResearchResult() { Success = false, Message = $"Errore {e.Message} nella chiamata API" };
    }
  }

  public async Task<AbortResult> AbortReport()
  {
    using var client = _clientFactory.CreateClient("FastApi");
    try
    {
      var response = await client.PostAsJsonAsync("abort_report", new { });
      if (!response.IsSuccessStatusCode)
        return new AbortResult() { Success = false, Message = $"Errore {response.StatusCode} nella chiamata API" };
        
      var result = await response.Content.ReadFromJsonAsync<AbortResult>();
      return result;
    }
    catch (Exception e)
    {
      return new AbortResult() { Success = false, Message = $"Errore {e.Message} nella chiamata API" };
    }
  }

  public async Task<PlanFeedbackResult> PlanFeedback(string feedback)
  {
    using var client = _clientFactory.CreateClient("FastApi");
    try
    {
      var response = await client.PostAsJsonAsync("feedback_plan", new PlanFeedbackRequest() { Feedback = feedback});
      if (!response.IsSuccessStatusCode)
        return new PlanFeedbackResult { Success = false, Message = $"Errore {response.StatusCode} nella chiamata API" };

      var result = await response.Content.ReadFromJsonAsync<PlanFeedbackResult>();
      return result;
    }
    catch (Exception e)
    {
      return new PlanFeedbackResult() { Success = false, Message = $"Errore {e.Message} nella chiamata API" };
    }
  }


  public async Task<ApprovePlanResult> ApprovePlan()
  {
    using var client = _clientFactory.CreateClient("FastApi");
    try
    {
      var response = await client.PostAsJsonAsync("approve_plan",new{});
      if (!response.IsSuccessStatusCode)
        return new ApprovePlanResult() { Success = false, Message = $"Errore {response.StatusCode} nella chiamata API" };

      var result = await response.Content.ReadFromJsonAsync<ApprovePlanResult>();
      return result;
    }
    catch (Exception e)
    {
      return new ApprovePlanResult() { Success = false, Message = $"Errore {e.Message} nella chiamata API" };
    }
  }

  public class ResearchRequest
  {
    public string Topic { get; set; }
    public DeepResearchConfig Config { get; set; }
  }

  public class PlanFeedbackRequest
  {
    public string Feedback { get; set; }
  }

  public class BaseRsult
  {
    public bool Success { get; set; }
    public string Message { get; set; }
  }


  public class ResearchResult:BaseRsult
  {
    public string Topic { get; set; }
  }


  public class ApprovePlanResult: BaseRsult
  {
  }
  
  public class AbortResult: BaseRsult
  {
  }

  public class PlanFeedbackResult: BaseRsult
  {
      
  }

  
}