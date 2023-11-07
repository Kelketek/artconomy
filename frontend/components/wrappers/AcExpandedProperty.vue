<template>
  <v-dialog v-model="toggle" :width="width" :transition="transition" :fullscreen="fullscreen" :eager="eager"
            :attach="$modalTarget">
    <v-card tile>
      <v-toolbar flat dark color="secondary" :dense="$vuetify.display.mdAndUp">
        <v-toolbar-title>
          <slot name="title"/>
        </v-toolbar-title>
        <v-spacer/>
        <v-btn icon @click="toggle = false" dark class="dialog-closer">
          <v-icon icon="mdi-close"/>
        </v-btn>
      </v-toolbar>
      <ac-form @submit.prevent="toggle=false">
        <v-card-text class="scrollableText">
          <slot/>
        </v-card-text>
        <v-card-actions>
          <slot name="actions">
            <v-spacer/>
            <v-btn color="primary" variant="flat" type="submit">
              Done
            </v-btn>
          </slot>
        </v-card-actions>
      </ac-form>
    </v-card>
  </v-dialog>
</template>

<script lang="ts">
import {Component, mixins, Prop, toNative} from 'vue-facing-decorator'
import Dialog from '@/mixins/dialog'
import AcForm from '@/components/wrappers/AcForm.vue'

@Component({
  components: {AcForm},
})
class AcExpandedProperty extends mixins(Dialog) {
  @Prop({default: true})
  public eager!: boolean
}

export default toNative(AcExpandedProperty)
</script>
