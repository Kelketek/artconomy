<template>
  <v-dialog v-model="toggle" :width="width" :transition="transition" :fullscreen="fullscreen" :eager="true">
    <v-card tile>
      <v-toolbar flat dark color="secondary" :dense="$vuetify.breakpoint.mdAndUp">
        <v-toolbar-title><slot name="title" /></v-toolbar-title>
        <v-spacer/>
        <v-btn icon @click.native="toggle = false" dark class="dialog-closer">
          <v-icon>close</v-icon>
        </v-btn>
      </v-toolbar>
      <ac-form @submit.prevent="toggle=false">
        <v-card-text class="scrollableText">
          <slot />
        </v-card-text>
        <v-card-actions>
          <slot name="actions">
            <v-spacer />
            <v-btn color="primary" type="submit">
              Done
            </v-btn>
          </slot>
        </v-card-actions>
      </ac-form>
    </v-card>
  </v-dialog>
</template>

<script lang="ts">
import Component, {mixins} from 'vue-class-component'
import Dialog from '@/mixins/dialog'
import AcForm from '@/components/wrappers/AcForm.vue'
@Component({
  components: {AcForm},
})
export default class AcExpandedProperty extends mixins(Dialog) {
}
</script>
