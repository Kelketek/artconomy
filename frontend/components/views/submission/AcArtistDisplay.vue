<template>
  <ac-load-section :controller="controller">
    <v-row dense>
      <v-tooltip
        v-if="editable"
        top
        aria-label="Tooltip for Artist tagger"
      >
        <template #activator="{props}">
          <v-btn
            v-bind="props"
            color="secondary"
            icon
            size="small"
            class="mr-1"
            aria-label="Tag Artists"
            @click="toggle=true"
          >
            <v-icon
              :icon="mdiPalette"
              size="x-large"
            />
          </v-btn>
        </template>
        Edit Artists
      </v-tooltip>
      <v-tooltip
        v-else
        top
        aria-label="Tooltip for Artists"
      >
        <template #activator="{props}">
          <v-icon
            v-bind="props"
            :icon="mdiPalette"
          />
        </template>
        Artists
      </v-tooltip>
      <v-col
        v-if="controller.empty"
        align-self="center"
      >
        No artists tagged.
      </v-col>
      <ac-avatar
        v-for="artist in controller.list"
        :key="artist.x!.id"
        :user="artist.x!.user"
        class="mr-1"
      />
      <ac-expanded-property
        v-if="editable"
        v-model="toggle"
        aria-label="Artist tagging dialog"
      >
        <template #title>
          Artists
        </template>
        <ac-related-manager
          :field-controller="tagArtist.fields.user_id"
          :list-controller="controller"
          item-key="user"
        >
          <template #preview="{item}">
            <ac-avatar
              :user="item.x.user"
              :removable="true"
              class="mr-1"
              @remove="item.delete().catch(tagArtist.setErrors)"
            />
          </template>
          <template #default="{filter}">
            <v-row class="mt-1">
              <v-col cols="12">
                <ac-bound-field
                  label="Tag Artist"
                  :autofocus="true"
                  hint="Enter the username of another Artconomy user to tag them as an artist."
                  :field="tagArtist.fields.user_id"
                  field-type="ac-user-select"
                  :multiple="false"
                  :filter="filter"
                  :tagging="true"
                />
              </v-col>
            </v-row>
          </template>
        </ac-related-manager>
      </ac-expanded-property>
    </v-row>
  </ac-load-section>
</template>

<script setup lang="ts">
import AcLoadSection from '../../wrappers/AcLoadSection.vue'
import AcRelatedManager from '../../wrappers/AcRelatedManager.vue'
import AcAvatar from '../../AcAvatar.vue'
import {ListController} from '@/store/lists/controller.ts'
import AcExpandedProperty from '@/components/wrappers/AcExpandedProperty.vue'
import AcBoundField from '@/components/fields/AcBoundField.ts'
import {mdiPalette} from '@mdi/js'
import {ref} from 'vue'
import {useForm} from '@/store/forms/hooks.ts'
import type {ArtistTag} from '@/types/main'

const props = defineProps<{controller: ListController<ArtistTag>, submissionId: number|string, editable: boolean}>()

const toggle = ref(false)

const tagArtist = useForm(props.controller.name.value + '__tagArtist', {
  fields: {user_id: {value: null}},
  endpoint: props.controller.endpoint,
})
</script>
