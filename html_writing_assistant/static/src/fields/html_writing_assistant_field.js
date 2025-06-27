/** @odoo-module **/

import { htmlField, HtmlField } from "@html_editor/fields/html_field";
import {
  Component,
  useState,
  useRef,
  onMounted,
  onWillUnmount,
} from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { rpc } from "@web/core/network/rpc";
import { _t } from "@web/core/l10n/translation";

export class HtmlWritingAssistantField extends HtmlField {
  static template = "html_writing_assistant.HtmlWritingAssistantField";

  setup() {
    super.setup();

    this.notification = useService("notification");

    this.assistantState = useState({
      suggestions: [],
      isAnalyzing: false,
      error: "",
      activeCategory: "all",
      showSuggestions: false,
      activeTooltip: null,
      tooltipPosition: { top: 0, left: 0, isBelow: false },
    });

    this.categories = [
      { id: "all", label: _t("All"), color: "text-primary" },
      { id: "grammar", label: _t("Grammar"), color: "text-info" },
      { id: "spelling", label: _t("Spelling"), color: "text-danger" },
      { id: "punctuation", label: _t("Punctuation"), color: "text-warning" },
      { id: "style", label: _t("Style"), color: "text-success" },
      { id: "clarity", label: _t("Clarity"), color: "text-secondary" },
    ];

    // Event handlers bound to this
    this.boundOnEditorClick = this.onEditorClick.bind(this);
    this.boundOnDocumentClick = this.onDocumentClick.bind(this);

    onMounted(() => {
      // Set up document click handler
      document.addEventListener("click", this.boundOnDocumentClick);
    });

    onWillUnmount(() => {
      this.cleanupAssistantFeatures();
    });
  }

  setupAssistantFeatures() {
    // Set up click handlers for highlighted suggestions
    if (this.editor && this.editor.editable) {
      this.editor.editable.addEventListener("click", this.boundOnEditorClick);
    }
  }

  cleanupAssistantFeatures() {
    if (this.editor && this.editor.editable) {
      this.editor.editable.removeEventListener(
        "click",
        this.boundOnEditorClick
      );
    }
    document.removeEventListener("click", this.boundOnDocumentClick);
  }

  onDocumentClick(event) {
    // Close tooltip if clicking outside
    if (!event.target.closest(".o_writing_assistant_tooltip")) {
      this.assistantState.activeTooltip = null;
    }
  }

  onEditorClick(event) {
    if (event.target.classList.contains("o_suggestion_highlight")) {
      this.showTooltipForSuggestion(event.target, event);
    } else {
      this.assistantState.activeTooltip = null;
    }
  }

  showTooltipForSuggestion(element, event) {
    const suggestionId = element.dataset.suggestionId;
    const suggestion = this.assistantState.suggestions.find(
      (s) => s.id === suggestionId
    );

    if (!suggestion) return;

    // Calculate tooltip position relative to the editor
    const rect = element.getBoundingClientRect();
    const editorRect = this.editor.editable.getBoundingClientRect();

    let top = rect.top - editorRect.top - 10;
    let left = rect.left - editorRect.left + rect.width / 2;
    let isBelow = false;

    if (top < 100) {
      top = rect.bottom - editorRect.top + 10;
      isBelow = true;
    }

    this.assistantState.tooltipPosition = { top, left, isBelow };
    this.assistantState.activeTooltip = suggestion;

    event.preventDefault();
    event.stopPropagation();
  }

  async analyzeText() {
    if (!this.editor || !this.editor.editable) {
      this.assistantState.error = _t("Editor not ready");
      return;
    }

    const content = this.editor.getContent();
    if (!content || !content.trim()) {
      this.assistantState.error = _t("Please enter some text to analyze");
      return;
    }

    this.assistantState.isAnalyzing = true;
    this.assistantState.error = "";
    this.assistantState.suggestions = [];

    try {
      const suggestions = await rpc("/web/html_writing_assistant/analyze", {
        text: content,
      });

      // Add unique IDs to suggestions for tracking
      this.assistantState.suggestions = suggestions.map(
        (suggestion, index) => ({
          ...suggestion,
          id: `suggestion_${index}_${Date.now()}`,
        })
      );

      this.assistantState.showSuggestions = true;
      this.applyHighlights();

      if (suggestions.length === 0) {
        this.notification.add(
          _t("Great! No suggestions found. Your text looks good!"),
          {
            type: "success",
          }
        );
      } else {
        this.notification.add(_t(`Found ${suggestions.length} suggestion(s)`), {
          type: "info",
        });
      }
    } catch (error) {
      console.error("Analysis error:", error);
      this.assistantState.error = _t(
        "Failed to analyze text. Please try again."
      );
    } finally {
      this.assistantState.isAnalyzing = false;
    }
  }

  applyHighlights() {
    if (
      !this.editor ||
      !this.editor.editable ||
      this.assistantState.suggestions.length === 0
    ) {
      return;
    }

    let content = this.editor.getContent();

    // Remove existing highlights
    content = content.replace(
      /<span class="o_suggestion_highlight"[^>]*>(.*?)<\/span>/g,
      "$1"
    );

    // Apply new highlights
    this.assistantState.suggestions.forEach((suggestion) => {
      const categoryColors = {
        grammar: "#e3f2fd",
        spelling: "#ffebee",
        punctuation: "#fff3e0",
        style: "#e8f5e8",
        clarity: "#f3e5f5",
      };

      const color = categoryColors[suggestion.category] || "#f5f5f5";
      const issue = this.escapeRegex(suggestion.issue);

      const regex = new RegExp(`\\b${issue}\\b`, "gi");
      content = content.replace(regex, (match) => {
        return `<span class="o_suggestion_highlight" 
                              data-suggestion-id="${suggestion.id}"
                              style="background-color: ${color}; padding: 2px 4px; border-radius: 3px; cursor: pointer; border-bottom: 2px solid ${this.getCategoryBorderColor(
          suggestion.category
        )};"
                              title="${
                                suggestion.explanation
                              }">${match}</span>`;
      });
    });

    // Use the editor's content setting method
    if (this.editor.editable) {
      this.editor.editable.innerHTML = content;
    }
  }

  getCategoryBorderColor(category) {
    const colors = {
      grammar: "#2196f3",
      spelling: "#f44336",
      punctuation: "#ff9800",
      style: "#4caf50",
      clarity: "#9c27b0",
    };
    return colors[category] || "#757575";
  }

  escapeRegex(string) {
    return string.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  }

  async applySuggestion(suggestion) {
    if (!this.editor) return;

    try {
      const currentContent = this.editor.getContent();
      const result = await rpc("/web/html_writing_assistant/apply_suggestion", {
        content: currentContent,
        suggestion: suggestion,
      });

      if (result.success) {
        // Update editor content
        if (this.editor.editable) {
          this.editor.editable.innerHTML = result.content;
        }

        // Remove the applied suggestion from the list
        this.assistantState.suggestions =
          this.assistantState.suggestions.filter((s) => s.id !== suggestion.id);

        // Close tooltip
        this.assistantState.activeTooltip = null;

        // Re-apply highlights for remaining suggestions
        this.applyHighlights();

        this.notification.add(_t("Suggestion applied successfully"), {
          type: "success",
        });

        // Trigger change to mark field as dirty
        this.onChange();
      } else {
        this.notification.add(
          _t("Failed to apply suggestion: ") +
            (result.error || "Unknown error"),
          {
            type: "danger",
          }
        );
      }
    } catch (error) {
      console.error("Apply suggestion error:", error);
      this.notification.add(_t("Failed to apply suggestion"), {
        type: "danger",
      });
    }
  }

  dismissSuggestion(suggestion) {
    this.assistantState.suggestions = this.assistantState.suggestions.filter(
      (s) => s.id !== suggestion.id
    );

    if (
      this.assistantState.activeTooltip &&
      this.assistantState.activeTooltip.id === suggestion.id
    ) {
      this.assistantState.activeTooltip = null;
    }

    this.applyHighlights();
  }

  async applyAllSuggestions() {
    const suggestions = [...this.assistantState.suggestions];
    let successCount = 0;

    for (const suggestion of suggestions) {
      try {
        const currentContent = this.editor.getContent();
        const result = await rpc(
          "/web/html_writing_assistant/apply_suggestion",
          {
            content: currentContent,
            suggestion: suggestion,
          }
        );

        if (result.success) {
          if (this.editor.editable) {
            this.editor.editable.innerHTML = result.content;
          }
          successCount++;
        }
      } catch (error) {
        console.error("Error applying suggestion:", error);
      }
    }

    // Clear all suggestions and highlights
    this.assistantState.suggestions = [];
    this.assistantState.activeTooltip = null;
    this.applyHighlights();

    this.notification.add(
      _t(`Applied ${successCount} out of ${suggestions.length} suggestions`),
      {
        type: successCount === suggestions.length ? "success" : "warning",
      }
    );

    // Trigger change to mark field as dirty
    this.onChange();
  }

  clearAllSuggestions() {
    this.assistantState.suggestions = [];
    this.assistantState.activeTooltip = null;
    this.applyHighlights();

    this.notification.add(_t("All suggestions cleared"), {
      type: "info",
    });
  }

  setActiveCategory(categoryId) {
    this.assistantState.activeCategory = categoryId;
  }

  get filteredSuggestions() {
    return this.assistantState.activeCategory === "all"
      ? this.assistantState.suggestions
      : this.assistantState.suggestions.filter(
          (s) => s.category === this.assistantState.activeCategory
        );
  }

  getCategoryColorClass(category) {
    const colors = {
      grammar: "text-info",
      spelling: "text-danger",
      punctuation: "text-warning",
      style: "text-success",
      clarity: "text-secondary",
    };
    return colors[category] || "text-muted";
  }

  toggleSuggestionsPanel() {
    this.assistantState.showSuggestions = !this.assistantState.showSuggestions;

    if (!this.assistantState.showSuggestions) {
      this.assistantState.activeTooltip = null;
    }
  }

  // Override the onEditorLoad to setup assistant features when editor is ready
  onEditorLoad(editor) {
    super.onEditorLoad(editor);
    this.setupAssistantFeatures();
  }

  // Override getConfig to add custom toolbar button
//   getConfig() {
//     const config = super.getConfig();

//     // Add writing assistant button to toolbar
//     if (!config.resources) {
//       config.resources = {};
//     }

//     config.resources = {
//       ...config.resources,
//       user_commands: [
//         ...(config.resources.user_commands || []),
//         {
//           id: "writing_assistant",
//           title: _t("Writing Assistant"),
//           icon: "fa-magic",
//           run: this.analyzeText.bind(this),
//         },
//       ],
//       toolbar_groups: {
//         ...(config.resources.toolbar_groups || {}),
//         writing_assistant: {
//           id: "writing_assistant",
//           sequence: 90,
//         },
//       },
//       toolbar_items: {
//         ...(config.resources.toolbar_items || {}),
//         writing_assistant: {
//           id: "writing_assistant",
//           groupId: "writing_assistant",
//           commandId: "writing_assistant",
//         },
//       },
//     };

//     return config;
//   }
}

registry
  .category("fields")
    .add("html_writing_assistant", {
        ...htmlField,
        component: HtmlWritingAssistantField
  });
