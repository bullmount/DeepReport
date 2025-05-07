using BlazorAnimation;
using DeepReport.Components;
using DeepReport.Services;
using Fluxor;
using MudBlazor.Services;

namespace DeepReport
{
  
  public class Program
  {
    public static void Main(string[] args)
    {
      var builder = WebApplication.CreateBuilder(args);

      // Add services to the container.
      builder.Services.AddRazorComponents()
        .AddInteractiveServerComponents();

      builder.Services.AddHttpClient("FastApi", client =>
      {
        client.BaseAddress = new Uri("http://127.0.0.1:8123/"); // URL API Python
      });
      builder.Services.AddFluxor(options =>
      {
        options.ScanAssemblies(typeof(Program).Assembly, typeof(DeepReportApiController).Assembly);
      });

      builder.Services.AddSingleton<IEventAggregator,EventAggregator>();
      builder.Services.AddScoped<IDeepReportSvc,DeepReportSvc>();
      builder.Services.AddScoped<DeepResearchConfig>();

      builder.Services.AddMudServices();
      
      builder.Services.AddControllers();
      builder.Services.Configure<AnimationOptions>(Guid.NewGuid().ToString(), c => { });

      var app = builder.Build();

      // Configure the HTTP request pipeline.
      if (!app.Environment.IsDevelopment())
      {
        app.UseExceptionHandler("/Error");
        // The default HSTS value is 30 days. You may want to change this for production scenarios, see https://aka.ms/aspnetcore-hsts.
        app.UseHsts();
      }

      app.UseHttpsRedirection();

      app.UseAntiforgery();

      app.MapControllers(); // <<== aggiungi questa riga

      app.MapStaticAssets();
      app.MapRazorComponents<App>()
        .AddInteractiveServerRenderMode();


      app.Run();
    }
  }
}