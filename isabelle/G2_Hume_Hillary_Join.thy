theory G2_Hume_Hillary_Join
  imports Main
begin

(* Independent Isabelle/HOL research lane. This does not import or certify Lean.
  Six X3 fields correspond by name to OriginalX3Full.lean. The meaning of
  these fields, actual-event coverage, and the Hume ethical bridge remain
  separate proof obligations. Koru is not modelled as a numeric function. *)

locale g2_hume_hillary =
  fixes owed :: "'event \<Rightarrow> 'person \<Rightarrow> bool"
    and enacted :: "'event \<Rightarrow> bool"
    and continues :: "'event \<Rightarrow> 'person \<Rightarrow> bool"
    and authorized :: "'event \<Rightarrow> 'person \<Rightarrow> bool"
    and free :: "'event \<Rightarrow> 'person \<Rightarrow> bool"
    and restrained :: "'event \<Rightarrow> 'person \<Rightarrow> bool"
    and maximal :: "'event \<Rightarrow> 'person \<Rightarrow> bool"
    and provenanced :: "'event \<Rightarrow> 'person \<Rightarrow> bool"
    and offered :: "'event \<Rightarrow> 'person \<Rightarrow> 'person \<Rightarrow> bool"
    and accepted :: "'event \<Rightarrow> 'person \<Rightarrow> 'person \<Rightarrow> bool"
    and benefits :: "'event \<Rightarrow> 'person \<Rightarrow> bool"
begin

definition original_six where
  "original_six e p \<longleftrightarrow>
    continues e p \<and> authorized e p \<and> free e p \<and>
    restrained e p \<and> maximal e p \<and> provenanced e p"

definition reciprocal_hand where
  "reciprocal_hand e p q \<longleftrightarrow>
    p \<noteq> q \<and> offered e p q \<and> accepted e q p"

definition g2_gift where
  "g2_gift e p q \<longleftrightarrow>
    enacted e \<and> owed e p \<and> owed e q \<and>
    reciprocal_hand e p q \<and>
    original_six e p \<and> original_six e q \<and>
    benefits e p \<and> benefits e q"

lemma gift_preserves_both_original_six:
  assumes "g2_gift e p q"
  shows "original_six e p \<and> original_six e q"
  using assms unfolding g2_gift_def by blast

lemma gift_requires_authentic_acceptance:
  assumes "g2_gift e p q"
  shows "offered e p q \<and> accepted e q p"
  using assms unfolding g2_gift_def reciprocal_hand_def by blast

end
end
