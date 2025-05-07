using DeepReport.Services;
using DeepReport.Store;
using Fluxor;
using Fluxor.Blazor.Web.Components;
using Microsoft.AspNetCore.Components;
using MudBlazor;
using System.Text.RegularExpressions;

namespace DeepReport.Components.Pages;

public partial class Home : FluxorComponent
{
  private string Risultato;
  [Inject] public IState<DeepResearchState> _deepResearchState { get; set; }
  [Inject] private NavigationManager _navman { get; set; }
  [Inject] private IDispatcher Dispatcher { get; set; }
  [Inject] private IDialogService DialogService { get; set; }

  [Inject] private DeepResearchConfig _config { get; set; }

  private string _topic = ""; // "prossimo referendum 2025 italia"; 
  private bool _domini_specifici;
  private List<string> _domains = [];

  protected override async Task OnInitializedAsync()
  {
    await base.OnInitializedAsync();

    SubscribeToAction<DeepResearchReducersActions.SetErrorAction>(OnSetError);
    SubscribeToAction<DeepResearchReducersActions.SetStateAction>(OnSetState);
  }


  private void OnSetState(DeepResearchReducersActions.SetStateAction obj)
  {
    if (obj.state is >= EReportState.Started and < EReportState.Aborted)
      _navman.NavigateTo("deepresearch");
  }


  private async void OnSetError(DeepResearchReducersActions.SetErrorAction obj)
  {
    await DialogService.ShowMessageBox("Errore", obj.Message, yesText: "Chiudi");
  }

  private async Task SendRequest()
  {
    if (string.IsNullOrWhiteSpace(_topic))
    {
      await DialogService.ShowMessageBox("Argomento non specificato", "Occorre specificare l'argomento per il report");
      return;
    }

    _config.sites_search_restriction = _domains;
    Dispatcher.Dispatch(new DeepResearchEffectsActions.SetTopicAction(_topic, _config));
  }

  private async Task OnAddDominio()
  {
    var res = await DlgInputBox.Show(DialogService, 
      title: "Nuovo dominio",
      caption: "Inserisci il nome di un diminio (es. wikipedia.it):",
      okButtonLabel:"Aggiungi",
      helpText:"Nome del dominio",validateFunc:CheckDomain);
    if (!string.IsNullOrWhiteSpace(res))
      if (_domains.All(x => !string.Equals(x, res, StringComparison.CurrentCultureIgnoreCase)))
        _domains.Add(res.ToLower());
  }

  private string CheckDomain(string domain)
  {
    var regex = new Regex(@"^(?!-)[A-Za-z0-9-]{1,63}(?<!-)(\.[A-Za-z]{2,})+$");
    if (regex.IsMatch(domain))
      return string.Empty;
    return "Nome di dominio non valido.";
  }

  private void OnRemoveDomain(string domain)
  {
    _domains.RemoveAll(x => x.ToLower() == domain.ToLower());
  }
}