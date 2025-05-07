using Microsoft.AspNetCore.Components;
using System.Text.Json;
using DeepReport.Store;
using Fluxor.Blazor.Web.Components;
using Fluxor;
using MudBlazor;
using Markdig;
using DeepReport.Services;


namespace DeepReport.Components.Pages;

public partial class DeepResearch : FluxorComponent
{
  [Inject] private NavigationManager _navMan { get; set; }
  [Inject] private IDispatcher Dispatcher { get; set; }
  [Inject] public IState<DeepResearchState> _deepResearchState { get; set; }
  [Inject] private IDialogService _dlgSvc { get; set; }
  [Inject] private IDeepReportSvc _deepReportSvc { get; set; }

  private List<string> _planning = [];
  private MarkupString? _report_finale;
  private bool _in_revisione_finale;
    
  protected override Task OnInitializedAsync()
  {
    SubscribeToAction<DeepResearchReducersActions.SetStateAction>(OnSetState);
    SubscribeToAction<DeepResearchReducersActions.SetSezioneStateAction>(OnSetSezioneState);
    return base.OnInitializedAsync();
  }

  private void OnSetSezioneState(DeepResearchReducersActions.SetSezioneStateAction obj)
  {
    StateHasChanged();
  }

  private static T? ParseEventData<T>(string json) where T : new()
  {
    if (string.IsNullOrEmpty(json))
      return new T();
    var options = new JsonSerializerOptions { PropertyNameCaseInsensitive = true };
    return JsonSerializer.Deserialize<T>(json, options);
  }


  private async void OnSetState(DeepResearchReducersActions.SetStateAction obj)
  {
    if (obj.state is EReportState.Searching or EReportState.Planning)
    {
      _planning.Add(obj.eventData.message);
    }
    else if (obj.state == EReportState.WaitingForApproval)
    {
      var elenco = ParseEventData<PropostaSezioni>(obj.eventData.data);
      if (elenco.Sezioni.Any())
      {
        var dlg = DlgSectionApproval.Show(_dlgSvc, elenco);
        var res = await dlg.Result;
        if (res.Data is DlgSectionApproval.Result r && r.Feedback)
          _planning = [];
      }
    }
    else if (obj.state == EReportState.Approved)
    {
      var elenco = ParseEventData<PropostaSezioni>(obj.eventData.data);
      Dispatcher.Dispatch(new DeepResearchReducersActions.SetSezioniAction(elenco.Sezioni));
    }
    else if (obj.state == EReportState.WritingSection)
    {
      var datiSezione = ParseEventData<SectionData>(obj.eventData.data);
      Dispatcher.Dispatch(new DeepResearchReducersActions.SetSezioneStateAction(obj.eventData.message, datiSezione));
    }
    else if (obj.state == EReportState.Error || obj.state == EReportState.Aborted)
    {
      _navMan.NavigateTo("/");
    }
    else if (obj.state == EReportState.Reviewing)
    {
      _in_revisione_finale = true;
    }
    else if (obj.state == EReportState.Completed)
    {
      var report = ParseEventData<ReportFinale>(obj.eventData.data);
      var pipeline = new MarkdownPipelineBuilder()
        .UseAdvancedExtensions() 
        .Build();
      _report_finale = new MarkupString(Markdown.ToHtml(report.final_report));
    }

    StateHasChanged();
  }


  private string GetRevisione(ReportSection sezione)
  {
    if (!sezione.Richiede_ricerca)
      return sezione.Fase == null ? "---" : "Revisione 1";

    var n = sezione.SearchIterations;
    if (sezione.Fase <= EFaseSezioneFase.SEARCH)
      n++;
    return $"Revisione {n}";
  }

  private string GetImageSection(ReportSection sezione)
  {
    if (!sezione.Richiede_ricerca)
    {
      return sezione.Fase switch
      {
        EFaseSezioneFase.WRITE => "/images/writing.gif",
        EFaseSezioneFase.COMPLETE => "/images/report_completed.png",
        _ => ""
      };
    }

    return sezione.Fase switch
    {
      EFaseSezioneFase.SEARCH => "/images/web_search.gif",
      EFaseSezioneFase.QUERY => "/images/query1.gif",
      EFaseSezioneFase.WRITE => "/images/writing.gif",
      EFaseSezioneFase.COMPLETE => "/images/report_completed.png",
      _ => ""
    };
  }

  private void NewReport()
  {
    _navMan.NavigateTo("/");
  }

  private async Task OnClickAbort()
  {
    Dispatcher.Dispatch(new DeepResearchEffectsActions.AbortReportAction());
  }
}