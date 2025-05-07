using DeepReport.Services;

namespace DeepReport.Store;

public abstract class DeepResearchEffectsActions
{
  public record SetTopicAction(string Topic, DeepResearchConfig DeepResearchConfig);

  public record AbortReportAction;
}