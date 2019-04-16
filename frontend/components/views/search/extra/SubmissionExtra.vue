<template>
  <v-flex xs12 text-xs-center class="pt-2" v-if="isRegistered">
    <v-expansion-panel v-model="panel">
      <v-expansion-panel-content>
        <span slot="header"><v-icon left>settings</v-icon>Search Options</span>
        <v-card-text>
          <v-layout row wrap>
            <v-flex xs12 sm6 md4>
              <ac-bound-field
                  :field="searchForm.fields.watch_list"
                  field-type="v-checkbox"
                  label="Watch List"
                  :persistent-hint="true"
                  hint="Only return results from artists on my watch list."
              />
            </v-flex>
          </v-layout>
        </v-card-text>
      </v-expansion-panel-content>
    </v-expansion-panel>
  </v-flex>
</template>

<script lang="ts">
import Component, {mixins} from 'vue-class-component'
import SearchHints from '../mixins/SearchHints'
import AcBoundField from '@/components/fields/AcBoundField'
import Viewer from '@/mixins/viewer'
  @Component({
    components: {AcBoundField},
  })
export default class SubmissionExtra extends mixins(SearchHints, Viewer) {
    public panel: null|number = null
    public created() {
      if (this.searchForm.rawData.watch_list) {
        // Expansion panel is zero indexed, so this will expand the panel. Null is none expanded.
        this.panel = 0
      }
    }
}
</script>
