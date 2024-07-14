<template>
  <div>
    <div id="sfw_mode">{{subjectHandler.user.patchers.sfw_mode.model}}</div>
    <div id="max_load">{{subjectHandler.artistProfile.patchers.max_load.model}}</div>
  </div>
</template>

<script setup lang="ts">
import {genArtistProfile} from '@/specs/helpers/fixtures.ts'
import DeliverableViewSettings from '@/types/DeliverableViewSettings.ts'
import {useSingle} from '@/store/singles/hooks.ts'
import {useProfile} from '@/store/profiles/hooks.ts'

const subjectHandler = useProfile('Fox')
subjectHandler.artistProfile.makeReady(genArtistProfile())
const localShare = useSingle<DeliverableViewSettings>('TestSingle', {endpoint: '#'})
defineExpose({localShare})
</script>
