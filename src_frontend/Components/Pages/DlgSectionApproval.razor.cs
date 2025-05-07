using Microsoft.AspNetCore.Components;
using MudBlazor;
using DeepReport.Services;

namespace DeepReport.Components.Pages;

public partial class DlgSectionApproval : ComponentBase
{
  [Inject] private IDeepReportSvc _deepReportSvc { get; set; }
  [Inject] private IDialogService _dlgSvc{ get; set; }
  [CascadingParameter] private IMudDialogInstance MudDialog { get; set; }
  [Parameter,EditorRequired] public PropostaSezioni Proposta { get; set; } = new PropostaSezioni();

  private string _feedback = "";

  public static IDialogReference Show(IDialogService dlgSvc, PropostaSezioni proposta)
  {
    var parameters = new DialogParameters<DlgSectionApproval>
    {
      { "Proposta", proposta }
    };
    
    var dlgref = dlgSvc.Show<DlgSectionApproval>("Approvazione Sezione",parameters, new DialogOptions()
    {
      CloseButton = true,
      MaxWidth = MaxWidth.Medium,
      FullWidth = true,
      CloseOnEscapeKey = false,
      NoHeader = true,
      BackdropClick = false
    });
    return dlgref;
  }

  private async Task OnClickApprove()
  {
    var res  = await _deepReportSvc.ApprovePlan();
    if (res.Success)
      MudDialog.Close(DialogResult.Ok(new Result()));
  }

  private async Task OnClickSendFeedback()
  {
    if (string.IsNullOrWhiteSpace(_feedback))
      await _dlgSvc.ShowMessageBox("Feedback non valido", "Non è consentito inviare un feedback vuoto.");
    var res = await _deepReportSvc.PlanFeedback(_feedback);
    MudDialog.Close(DialogResult.Ok(new Result(){Feedback = true}));
  }

  private async Task OnClickAbort()
  {
    var res = await _deepReportSvc.AbortReport();
    if (res.Success)
      MudDialog.Close(DialogResult.Ok(new Result() { Aborted = true }));
  }

  public class Result
  {
    public bool Feedback { get; set; }
    public bool Aborted { get; set; }
  }
}

