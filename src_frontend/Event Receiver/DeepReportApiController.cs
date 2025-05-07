using Microsoft.AspNetCore.Mvc;
using DeepReport.Services;


namespace DeepReport;

[ApiController]
[Route("api/[controller]")]
public class DeepReportApiController : ControllerBase
{
  private readonly IEventAggregator _eventAggregator;

  public DeepReportApiController(IEventAggregator eventAggregator)
  {
    _eventAggregator = eventAggregator;
  }


  [HttpGet("health")] // Questo crea il sottopercorso /health
  public IActionResult Health()
  {
    return Ok(new { status = "healthy", timestamp = DateTime.UtcNow });
  }

  public class ResultData
  {
    public string Result { get; set; }
  }

  [HttpPost("SendEvent")]
  public async Task<ActionResult<SendEventResponse>> SendEvent([FromBody] EventData message)
  {
    _eventAggregator.Dispatch(message);
    var response = new SendEventResponse { Success = true };
    return Ok(response);
  }
}