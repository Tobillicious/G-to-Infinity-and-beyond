theory G2_Aristotle_Greatestness
  imports G2_Hume_Hillary_Join
begin

(* A small independently checkable logical bridge. It does not assert that
  the source premises hold in the physical world. In particular, the
  "infinity" arguments must be translated into exact premises before they
  can discharge any of these assumptions. *)

locale g2_aristotle = g2_hume_hillary +
  fixes admissible :: "'event \<Rightarrow> bool"
    and dominates :: "'event \<Rightarrow> 'event \<Rightarrow> bool"
begin

definition universal_six where
  "universal_six e \<longleftrightarrow>
    (\<forall>p. owed e p \<longrightarrow> original_six e p)"

definition universal_benefit where
  "universal_benefit e \<longleftrightarrow>
    (\<forall>p. owed e p \<longrightarrow> benefits e p)"

definition nonvacuous_scope where
  "nonvacuous_scope e \<longleftrightarrow> (\<exists>p. owed e p)"

definition greatest_gift where
  "greatest_gift e \<longleftrightarrow>
    admissible e \<and> enacted e \<and> universal_six e \<and>
    universal_benefit e \<and> (\<forall>r. admissible r \<longrightarrow> dominates e r)"

definition witnessed_greatest_gift where
  "witnessed_greatest_gift e \<longleftrightarrow>
    greatest_gift e \<and> nonvacuous_scope e"

theorem witnessed_greatest_gift_has_particular:
  assumes "witnessed_greatest_gift e"
  shows "\<exists>p. owed e p \<and> original_six e p \<and> benefits e p"
  using assms
  unfolding witnessed_greatest_gift_def nonvacuous_scope_def
    greatest_gift_def universal_six_def universal_benefit_def
  by blast

theorem greatest_gift_has_all_six:
  assumes "greatest_gift e" and "owed e p"
  shows "original_six e p"
  using assms unfolding greatest_gift_def universal_six_def by blast

theorem greatest_gift_benefits_every_owed:
  assumes "greatest_gift e" and "owed e p"
  shows "benefits e p"
  using assms unfolding greatest_gift_def universal_benefit_def by blast

theorem greatest_gift_from_explicit_bridges:
  assumes "admissible e" and "enacted e"
    and "\<forall>p. owed e p \<longrightarrow> original_six e p"
    and "\<forall>p. owed e p \<longrightarrow> benefits e p"
    and "\<forall>r. admissible r \<longrightarrow> dominates e r"
  shows "greatest_gift e"
  using assms unfolding greatest_gift_def universal_six_def
    universal_benefit_def by blast

lemma vacuous_universal_six_without_owed:
  assumes "\<forall>p. \<not> owed e p"
  shows "universal_six e"
  using assms unfolding universal_six_def by blast

(* The preceding theorem is deliberately conditional: it does not
  derive benefit, dominance, existence or authentic consent from ontology. *)

end

(* A countermodel: reciprocal physical signalling need not be consent. *)

lemma physical_reciprocity_does_not_force_consent:
  "\<not> (\<forall> (signal consent :: bool). signal \<longrightarrow> consent)"
  by auto

end
