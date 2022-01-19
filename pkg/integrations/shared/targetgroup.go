package shared

import (
	"encoding/json"

	"github.com/prometheus/common/model"
	"github.com/prometheus/prometheus/discovery/targetgroup"
)

// TargetGroup implements json.Marshaler for targetgroup.Group. This is
// required do to an issue with Prometheus: HTTP SD expects to be unmarshaled
// as JSON, but the form it expects to unmarshal the target groups in is not the form
// it marshals out to JSON as.
type TargetGroup targetgroup.Group

// MarshalJSON allows marshalling
func (tg *TargetGroup) MarshalJSON() ([]byte, error) {
	g := &struct {
		Targets []string       `json:"targets"`
		Labels  model.LabelSet `json:"labels,omitempty"`
	}{
		Targets: make([]string, 0, len(tg.Targets)),
		Labels:  tg.Labels,
	}
	for _, t := range tg.Targets {
		g.Targets = append(g.Targets, string(t[model.AddressLabel]))
	}
	return json.Marshal(g)
}