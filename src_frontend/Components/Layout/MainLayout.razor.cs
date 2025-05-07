using Microsoft.AspNetCore.Components;
using MudBlazor;
using MudBlazor.Utilities;

namespace DeepReport.Components.Layout
{
  public partial class MainLayout: LayoutComponentBase
  {
    private MudTheme _theme = new()
    {
      Typography = new Typography()
      {
        H5 = new H6Typography()
        {
          FontSize = "1.10rem",
          FontWeight = "500",
          LineHeight = "1.6",
          LetterSpacing = ".0075em",
        },
        H6 = new H6Typography()
        {
          FontSize = "1.0rem",
          FontWeight = "500",
          LineHeight = "1.6",
          LetterSpacing = ".0075em",
        }
      },
      PaletteLight = new PaletteLight()
      {
        AppbarBackground = MudColor.Parse("#0000A0"),
        Primary = MudColor.Parse("#0000A0"),
        Success = MudColor.Parse("#00943B")
      }

    };
  }
}
