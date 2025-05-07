using Microsoft.AspNetCore.Components;
using Microsoft.AspNetCore.Components.Web;
using MudBlazor;

namespace DeepReport.Components.Pages
{
  public partial class DlgInputBox : ComponentBase
  {
    private string _inputText = default!;
    [Inject]private IDialogService _dlgSvc { get; set; } = default!;
    [CascadingParameter] IMudDialogInstance MudDialog { get; set; }

    [Parameter] public string Title { get; set; } = "";
    [Parameter] public string Caption { get; set; } = "Immetti il testo:";
    [Parameter] public string DefaultText { get; set; } = default!;
    [Parameter] public string HelpText { get; set; } = default!;

    [Parameter] public int NumLines { get; set; } = 1;
    [Parameter] public string CancelButtonLabel { get; set; } = "Annulla";
    [Parameter] public string OkButtonLabel { get; set; } = "OK";
    [Parameter] public bool IsReadonly { get; set; }
    [Parameter] public bool TextIsRequired { get; set; }
    [Parameter] public IEnumerable<string> AutocompleteData { get; set; } = [];

    [Parameter] public Func<string, string>? ValidateFunc { get; set; } 

    protected override async Task OnParametersSetAsync()
    {
      _inputText = DefaultText;
      await base.OnParametersSetAsync();
    }

    public static async Task<string?> Show(IDialogService dlgSvc, string title, string caption, string helpText = "",
      int numLines = 1, string okButtonLabel = "OK", string cancelButtonLabel = "Annulla", bool isreadonly = false,
      bool textRequired = false, string defaultText = default!, IEnumerable<string>? autoCompleteData = null,
      Func<string,string>? validateFunc = null)
    {
      var prms = new DialogParameters<DlgInputBox>
      {
        { x => x.Title, title },
        { x => x.Caption, caption },
        { x => x.HelpText, helpText },
        { x => x.NumLines, numLines },
        { x => x.OkButtonLabel, okButtonLabel },
        { x => x.CancelButtonLabel, cancelButtonLabel },
        { x => x.IsReadonly, isreadonly },
        { x => x.TextIsRequired, textRequired },
        { x => x.DefaultText, defaultText },
        { x => x.AutocompleteData, autoCompleteData ?? [] },
        { x => x.ValidateFunc, validateFunc }
      };
      DialogOptions? options = new DialogOptions()
      {
        BackdropClick = false,
        CloseButton = false,
        FullWidth = true,
        MaxWidth = MaxWidth.Small,
        CloseOnEscapeKey = true,
        NoHeader = false,
      };
      var dlg = dlgSvc.Show<DlgInputBox>(title, prms, options);
      var res = await dlg.Result;
      if (res.Canceled)
        return null;
      return res.Data?.ToString();
    }


    void Submit()
    {
      if (ValidateFunc != null)
      {
        var res = ValidateFunc(_inputText);
        if (!string.IsNullOrEmpty(res))
        {
          _dlgSvc.ShowMessageBox("Dato non valido", res);
          return;
        }
      }
      MudDialog.Close(DialogResult.Ok(_inputText));
    }

    void Cancel()
    {
      MudDialog.Cancel();
    }


    private async Task OnKeyDown(KeyboardEventArgs args)
    {
      if (NumLines > 1) return;

      if (args.Key == "Enter")
      {
        await Task.Delay(100);
        Submit();
        StateHasChanged();
      }
    }

    private bool IsDisabled()
    {
      if (!TextIsRequired)
        return false;
      return string.IsNullOrWhiteSpace(_inputText);
    }

    private async Task<IEnumerable<string>> OnSearchAutoComplete(string arg1, CancellationToken arg2)
    {
      if (arg1.Length < 3)
        return AutocompleteData.ToList();
      return AutocompleteData.Where(x => x.Contains(arg1, StringComparison.InvariantCultureIgnoreCase));
    }
  }
}
